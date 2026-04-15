from app.models.session import SessionReport


class ReporterService:
    def generate(self, session_data: dict) -> SessionReport:
        """Genera un resumen completo de la sesión finalizada."""
        metrics_history = session_data.get("metrics_history", [])
        feedbacks_history = session_data.get("feedbacks_history", [])

        # Calcular promedios
        avg_posture = self._avg_field(metrics_history, ["posture", "score"])
        avg_eye_contact = self._avg_field(metrics_history, ["face", "eye_contact_pct"])
        avg_pace = self._avg_field(metrics_history, ["speech", "pace_wpm"])

        # Acumular fillers totales
        total_fillers: dict[str, int] = {}
        for m in metrics_history:
            words = m.get("speech", {}).get("fillers", {}).get("words", {})
            for word, count in words.items():
                total_fillers[word] = total_fillers.get(word, 0) + count

        # Generar recomendaciones
        recommendations = self._build_recommendations(
            avg_posture, avg_eye_contact, avg_pace, total_fillers,
        )

        # Resumen en texto
        duration = session_data.get("duration_seconds", 0)
        summary = self._build_summary(
            session_data["presenter_name"],
            duration,
            avg_posture,
            avg_eye_contact,
            avg_pace,
            total_fillers,
        )

        return SessionReport(
            session_id=session_data["id"],
            duration_seconds=duration,
            summary=summary,
            total_fillers=total_fillers,
            avg_posture_score=avg_posture,
            avg_eye_contact=avg_eye_contact,
            avg_pace_wpm=avg_pace,
            feedbacks=feedbacks_history,
            recommendations=recommendations,
        )

    def _avg_field(self, metrics: list[dict], keys: list[str]) -> float:
        values = []
        for m in metrics:
            val = m
            for k in keys:
                val = val.get(k, {}) if isinstance(val, dict) else 0
            if isinstance(val, (int, float)):
                values.append(val)
        return round(sum(values) / len(values), 2) if values else 0.0

    def _build_recommendations(
        self,
        posture: float,
        eye_contact: float,
        pace: float,
        fillers: dict[str, int],
    ) -> list[str]:
        recs = []

        if posture < 0.6:
            recs.append("Practica frente a un espejo manteniendo la espalda recta y hombros nivelados.")
        if eye_contact < 0.5:
            recs.append("Trabaja el contacto visual: elige 3 puntos en la sala y alterna la mirada entre ellos.")
        if pace > 170:
            recs.append("Tu ritmo es acelerado. Practica con pausas de 2 segundos entre ideas principales.")
        elif 0 < pace < 100:
            recs.append("Tu ritmo es algo lento. Intenta mantener un flujo más dinámico sin perder claridad.")

        total_filler_count = sum(fillers.values())
        if total_filler_count > 10:
            top = sorted(fillers.items(), key=lambda x: x[1], reverse=True)[:3]
            top_text = ", ".join([f"'{w}'" for w, _ in top])
            recs.append(f"Tus muletillas más frecuentes son {top_text}. Reemplázalas por pausas breves.")

        if not recs:
            recs.append("Excelente presentación. Sigue practicando para mantener este nivel.")

        return recs

    def _build_summary(
        self,
        name: str,
        duration: float,
        posture: float,
        eye_contact: float,
        pace: float,
        fillers: dict[str, int],
    ) -> str:
        minutes = int(duration / 60)
        total_fillers = sum(fillers.values())

        return (
            f"Resumen de la sesión de {name} ({minutes} min): "
            f"postura promedio {int(posture * 100)}%, "
            f"contacto visual {int(eye_contact * 100)}%, "
            f"ritmo {int(pace)} palabras/min, "
            f"{total_fillers} muletillas detectadas."
        )


reporter_service = ReporterService()