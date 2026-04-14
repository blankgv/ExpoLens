import time
import re

from app.config import settings
from app.models.metrics import SpeechMetrics, FillerMetrics


class AudioPipeline:
    def __init__(self):
        self._start_time = time.time()
        self._total_fillers = 0
        self._filler_detail: dict[str, int] = {}
        self._total_words = 0

        # Compilar patrón regex con las palabras de relleno
        escaped = [re.escape(w) for w in settings.filler_words]
        self._filler_pattern = re.compile(
            r'\b(' + '|'.join(escaped) + r')\b',
            re.IGNORECASE,
        )

    def process_transcript(self, text: str) -> SpeechMetrics:
        """Analiza un fragmento de transcripción."""
        words = text.split()
        self._total_words += len(words)

        # Detectar fillers
        matches = self._filler_pattern.findall(text.lower())
        for match in matches:
            self._total_fillers += 1
            self._filler_detail[match] = self._filler_detail.get(match, 0) + 1

        # Calcular ritmo (palabras por minuto)
        elapsed_minutes = (time.time() - self._start_time) / 60
        pace = self._total_words / elapsed_minutes if elapsed_minutes > 0 else 0

        # Fillers por minuto
        fillers_per_min = self._total_fillers / elapsed_minutes if elapsed_minutes > 0 else 0

        return SpeechMetrics(
            pace_wpm=round(pace, 1),
            transcript_chunk=text,
            fillers=FillerMetrics(
                count=self._total_fillers,
                per_minute=round(fillers_per_min, 1),
                words=dict(self._filler_detail),
            ),
        )

    def reset(self):
        """Reinicia las métricas para una nueva sesión."""
        self._start_time = time.time()
        self._total_fillers = 0
        self._filler_detail = {}
        self._total_words = 0