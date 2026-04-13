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