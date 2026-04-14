from pydantic import BaseModel


class FillerMetrics(BaseModel):
    count: int = 0
    per_minute: float = 0.0
    words: dict[str, int] = {}  # {"este": 5, "o sea": 3}


class SpeechMetrics(BaseModel):
    pace_wpm: float = 0.0
    transcript_chunk: str = ""
    fillers: FillerMetrics = FillerMetrics()


class PostureMetrics(BaseModel):
    score: float = 1.0  # 0.0 (mala) a 1.0 (buena)
    issues: list[str] = []


class GestureMetrics(BaseModel):
    repetitive_gestures: dict[str, int] = {}
    movement_level: str = "normal"  # "bajo", "normal", "excesivo"


class FaceMetrics(BaseModel):
    eye_contact_pct: float = 1.0
    detected_tics: list[str] = []
    nervousness_score: float = 0.0


class AggregatedMetrics(BaseModel):
    timestamp: float = 0.0
    window_seconds: float = 10.0
    posture: PostureMetrics = PostureMetrics()
    gestures: GestureMetrics = GestureMetrics()
    face: FaceMetrics = FaceMetrics()
    speech: SpeechMetrics = SpeechMetrics()