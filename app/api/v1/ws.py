import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.config import settings
from app.services.session import session_service
from app.pipelines.video import VideoPipeline
from app.pipelines.audio import AudioPipeline
from app.pipelines.aggregator import MetricsAggregator
from app.llm.engine import FeedbackEngine
from app.models.feedback import FeedbackResponse

router = APIRouter(tags=["streaming"])


@router.websocket("/stream/{session_id}")
async def stream(websocket: WebSocket, session_id: str):
    """Recibir frames video+audio y devolver feedback en tiempo real."""

    # Verificar API key
    api_key = websocket.headers.get("x-api-key")
    if api_key != settings.api_key:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="API key inválida")
        return

    # Verificar que la sesión existe
    try:
        await session_service.get(session_id)
    except KeyError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Sesión no encontrada")
        return

    await websocket.accept()
    await session_service.set_active(session_id)

    # Inicializar pipelines
    video_pipeline = VideoPipeline()
    audio_pipeline = AudioPipeline()
    aggregator = MetricsAggregator(window_seconds=settings.metrics_window_seconds)
    feedback_engine = FeedbackEngine()

    try:
        while True:
            data = await websocket.receive_bytes()

            if len(data) < 2:
                continue

            data_type = data[0]
            payload = data[1:]

            if data_type == 0x01:
                # Video frame
                video_metrics = video_pipeline.process_frame(payload)
                aggregator.push_video(video_metrics)

            elif data_type == 0x02:
                # Audio: el payload es texto transcrito (por ahora)
                transcript = payload.decode("utf-8", errors="ignore")
                if transcript.strip():
                    speech_metrics = audio_pipeline.process_transcript(transcript)
                    aggregator.push_audio(speech_metrics)

            # Verificar si toca generar feedback
            if aggregator.should_aggregate():
                metrics = aggregator.aggregate()
                feedbacks = feedback_engine.generate(metrics)

                response = FeedbackResponse(
                    session_id=session_id,
                    feedbacks=feedbacks,
                )

                await websocket.send_json(response.model_dump())

    except WebSocketDisconnect:
        video_pipeline.release()
        await session_service.finish(session_id)