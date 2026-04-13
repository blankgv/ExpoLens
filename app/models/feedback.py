from pydantic import BaseModel


class Feedback(BaseModel):
    timestamp: float
    severity: str  # "info", "warning", "critical"
    message: str
    category: str  # "postura", "fillers", "nerviosismo", "contacto_visual", "ritmo"


class FeedbackResponse(BaseModel):
    session_id: str
    feedbacks: list[Feedback] = []