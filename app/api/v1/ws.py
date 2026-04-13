from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.config import settings
from app.services.session import session_service
from app.models.session import SessionStatus

router = APIRouter(tags=["streaming"])


@router.websocket("/stream/{session_id}")
async def stream(websocket: WebSocket, session_id: str):
    """Recibir frames video+audio y devolver feedback en tiempo real."""

    # Verificar API key antes de aceptar la conexión
    api_key = websocket.headers.get("x-api-key")
    if api_key != settings.api_key:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="API key inválida")
        return

    # Verificar que la sesión existe
    try:
        session = await session_service.get(session_id)
    except KeyError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Sesión no encontrada")
        return

    await websocket.accept()

    # Marcar sesión como activa
    await session_service.set_active(session_id)

    try:
        while True:
            data = await websocket.receive_bytes()

            if len(data) < 2:
                continue

            # Primer byte indica el tipo de dato
            data_type = data[0]
            payload = data[1:]

            if data_type == 0x01:
                # Video frame → pipeline de video
                # TODO: CU-03 - procesar con MediaPipe
                pass
            elif data_type == 0x02:
                # Audio chunk → pipeline de audio
                # TODO: CU-04 - procesar con Whisper
                pass

            # TODO: CU-05 - cada N segundos, agregar métricas y enviar feedback
            # await websocket.send_json(feedback_response.model_dump())

    except WebSocketDisconnect:
        await session_service.finish(session_id)