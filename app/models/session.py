from enum import Enum

from pydantic import BaseModel


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    FINISHED = "finished"


class SessionCreate(BaseModel):
    presenter_name: str
    context: str


class SessionResponse(BaseModel):
    id: str
    status: SessionStatus
    presenter_name: str
    context: str
    created_at: float
    duration_seconds: float = 0.0


class SessionReport(BaseModel):
    session_id: str
    duration_seconds: float
    summary: str
    total_fillers: dict[str, int] = {}
    avg_posture_score: float = 0.0
    avg_eye_contact: float = 0.0
    avg_pace_wpm: float = 0.0
    feedbacks: list[dict] = []
    recommendations: list[str] = []