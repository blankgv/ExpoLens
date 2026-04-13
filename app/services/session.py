import time
import uuid

from app.models.session import SessionCreate, SessionResponse, SessionStatus


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
        }
        self._sessions[session_id] = session
        return self._to_response(session)

    async def get(self, session_id: str) -> SessionResponse:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        return self._to_response(session)

    async def finish(self, session_id: str) -> SessionResponse:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        session["status"] = SessionStatus.FINISHED
        return self._to_response(session)
    
    async def set_active(self, session_id: str) -> SessionResponse:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Sesión {session_id} no encontrada")
        session["status"] = SessionStatus.ACTIVE
        return self._to_response(session)

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