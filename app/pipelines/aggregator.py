import time

from app.models.metrics import (
    AggregatedMetrics,
    PostureMetrics,
    GestureMetrics,
    FaceMetrics,
    SpeechMetrics,
)


class MetricsAggregator:
    def __init__(self, window_seconds: float = 10.0):
        self.window_seconds = window_seconds
        self._video_buffer: list[dict] = []
        self._audio_buffer: list[SpeechMetrics] = []
        self._last_aggregate_time = time.time()

    def push_video(self, metrics: dict) -> None:
        """Agrega métricas de un frame de video."""
        self._video_buffer.append(metrics)

    def push_audio(self, metrics: SpeechMetrics) -> None:
        """Agrega métricas de un chunk de audio."""
        self._audio_buffer.append(metrics)

    def should_aggregate(self) -> bool:
        """Verifica si ya pasó el tiempo de la ventana."""
        return (time.time() - self._last_aggregate_time) >= self.window_seconds

    def aggregate(self) -> AggregatedMetrics:
        """Produce métricas promedio de la ventana actual y limpia los buffers."""
        now = time.time()

        posture = self._avg_posture()
        gestures = self._avg_gestures()
        face = self._avg_face()
        speech = self._latest_speech()

        # Limpiar buffers
        self._video_buffer.clear()
        self._audio_buffer.clear()
        self._last_aggregate_time = now

        return AggregatedMetrics(
            timestamp=now,
            window_seconds=self.window_seconds,
            posture=posture,
            gestures=gestures,
            face=face,
            speech=speech,
        )

    def _avg_posture(self) -> PostureMetrics:
        if not self._video_buffer:
            return PostureMetrics()

        scores = [m["posture"].score for m in self._video_buffer]
        all_issues = []
        for m in self._video_buffer:
            all_issues.extend(m["posture"].issues)

        # Issues más frecuentes
        unique_issues = list(set(all_issues))

        return PostureMetrics(
            score=round(sum(scores) / len(scores), 2),
            issues=unique_issues,
        )

    def _avg_gestures(self) -> GestureMetrics:
        if not self._video_buffer:
            return GestureMetrics()

        # Movimiento más frecuente
        levels = [m["gestures"].movement_level for m in self._video_buffer]
        movement = max(set(levels), key=levels.count)

        # Acumular gestos repetitivos
        all_gestures: dict[str, int] = {}
        for m in self._video_buffer:
            for gesture, count in m["gestures"].repetitive_gestures.items():
                all_gestures[gesture] = all_gestures.get(gesture, 0) + count

        return GestureMetrics(
            repetitive_gestures=all_gestures,
            movement_level=movement,
        )

    def _avg_face(self) -> FaceMetrics:
        if not self._video_buffer:
            return FaceMetrics()

        eye_contacts = [m["face"].eye_contact_pct for m in self._video_buffer]
        nervousness = [m["face"].nervousness_score for m in self._video_buffer]
        all_tics = []
        for m in self._video_buffer:
            all_tics.extend(m["face"].detected_tics)

        return FaceMetrics(
            eye_contact_pct=round(sum(eye_contacts) / len(eye_contacts), 2),
            detected_tics=list(set(all_tics)),
            nervousness_score=round(sum(nervousness) / len(nervousness), 2),
        )

    def _latest_speech(self) -> SpeechMetrics:
        if not self._audio_buffer:
            return SpeechMetrics()

        # Devolver las métricas más recientes (son acumulativas)
        return self._audio_buffer[-1]