import time
import uuid

from app.models.session import SessionCreate, SessionResponse, SessionStatus
from app.models.metrics import AggregatedMetrics


class SessionService:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    async def create(self, data: SessionCreate) -> SessionResponse:
        session_id = uuid.uuid4().hex[:12]
        session = {
            "id": session_id,
            "status": SessionStatus.CREATED,
            "presenter_name": data.presenter_name,
            "context": data.context,
            "created_at": time.time(),
            "metrics_history": [],
            "feedbacks_history": [],
        }
        self._sessions[session_id] = session
        return self._to_response(session)

    async def get(self, session_id: str) -> SessionResponse:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        return self._to_response(session)

    async def set_active(self, session_id: str) -> SessionResponse:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        session["status"] = SessionStatus.ACTIVE
        return self._to_response(session)

    async def finish(self, session_id: str) -> SessionResponse:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        session["status"] = SessionStatus.FINISHED
        return self._to_response(session)

    async def push_metrics(self, session_id: str, metrics: AggregatedMetrics) -> None:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        session["metrics_history"].append(metrics.model_dump())

    async def push_feedbacks(self, session_id: str, feedbacks: list[dict]) -> None:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        session["feedbacks_history"].extend(feedbacks)

    async def get_metrics(self, session_id: str) -> list[dict]:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        return session["metrics_history"]

    async def get_raw(self, session_id: str) -> dict:
        """Devuelve los datos internos de la sesión."""
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        return session

    def _to_response(self, session: dict) -> SessionResponse:
        duration = time.time() - session["created_at"]
        return SessionResponse(
            id=session["id"],
            status=session["status"],
            presenter_name=session["presenter_name"],
            context=session["context"],
            created_at=session["created_at"],
            duration_seconds=round(duration, 2),
        )


session_service = SessionService()