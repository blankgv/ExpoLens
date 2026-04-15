import time

from app.models.metrics import AggregatedMetrics
from app.models.feedback import Feedback


class FeedbackEngine:
    """Motor de feedback basado en reglas.

    Genera feedback constructivo analizando las métricas.
    En V2 se reemplazará por un LLM (Mistral/Llama).
    """

    def generate(self, metrics: AggregatedMetrics) -> list[Feedback]:
        feedbacks = []
        now = time.time()

        # Analizar postura
        if metrics.posture.score < 0.5:
            issues_text = ", ".join(metrics.posture.issues) if metrics.posture.issues else "postura incorrecta"
            feedbacks.append(Feedback(
                timestamp=now,
                severity="warning",
                category="postura",
                message=f"Tu postura necesita atención: {issues_text}. Intenta mantener la espalda recta y los hombros nivelados.",
            ))

        # Analizar contacto visual
        if metrics.face.eye_contact_pct < 0.5:
            feedbacks.append(Feedback(
                timestamp=now,
                severity="warning",
                category="contacto_visual",
                message=f"Tu contacto visual es bajo ({int(metrics.face.eye_contact_pct * 100)}%). Intenta mirar al tribunal por bloques de 3-5 segundos.",
            ))

        # Analizar nerviosismo
        if metrics.face.nervousness_score > 0.6:
            tics_text = ", ".join(metrics.face.detected_tics) if metrics.face.detected_tics else "señales de nerviosismo"
            feedbacks.append(Feedback(
                timestamp=now,
                severity="info",
                category="nerviosismo",
                message=f"Se detecta nerviosismo: {tics_text}. Respira profundo y haz una pausa breve.",
            ))

        # Analizar palabras de relleno
        if metrics.speech.fillers.per_minute > 3:
            top_fillers = sorted(
                metrics.speech.fillers.words.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:3]
            fillers_text = ", ".join([f"'{w}' ({c}x)" for w, c in top_fillers])
            severity = "critical" if metrics.speech.fillers.per_minute > 6 else "warning"
            feedbacks.append(Feedback(
                timestamp=now,
                severity=severity,
                category="fillers",
                message=f"Estás usando muchas muletillas ({metrics.speech.fillers.per_minute}/min): {fillers_text}. Reemplázalas por pausas breves.",
            ))

        # Analizar ritmo de habla
        if metrics.speech.pace_wpm > 170:
            feedbacks.append(Feedback(
                timestamp=now,
                severity="warning",
                category="ritmo",
                message=f"Estás hablando muy rápido ({int(metrics.speech.pace_wpm)} palabras/min). Baja el ritmo y respira entre ideas.",
            ))
        elif metrics.speech.pace_wpm > 0 and metrics.speech.pace_wpm < 100:
            feedbacks.append(Feedback(
                timestamp=now,
                severity="info",
                category="ritmo",
                message=f"Tu ritmo es algo lento ({int(metrics.speech.pace_wpm)} palabras/min). Intenta mantener un flujo más dinámico.",
            ))

        # Analizar gestos
        if metrics.gestures.movement_level == "excesivo":
            feedbacks.append(Feedback(
                timestamp=now,
                severity="warning",
                category="gestos",
                message="Tus movimientos son excesivos. Intenta mantener las manos a la altura del torso con gestos controlados.",
            ))
        elif metrics.gestures.movement_level == "bajo":
            feedbacks.append(Feedback(
                timestamp=now,
                severity="info",
                category="gestos",
                message="Estás muy estático. Usa las manos para enfatizar puntos clave de tu presentación.",
            ))

        # Si todo está bien
        if not feedbacks:
            feedbacks.append(Feedback(
                timestamp=now,
                severity="info",
                category="general",
                message="¡Vas muy bien! Mantén este ritmo.",
            ))

        return feedbacks