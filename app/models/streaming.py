from pydantic import BaseModel


class StreamFrame(BaseModel):
    """Mensaje que llega por WebSocket."""
    type: str  # "video" o "audio"
    data: str  # bytes codificados en base64
    timestamp: float


class StreamFeedback(BaseModel):
    """Mensaje que ExpoLens devuelve por WebSocket."""
    session_id: str
    timestamp: float
    feedbacks: list[dict] = []
    metrics: dict = {}