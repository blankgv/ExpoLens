from fastapi import APIRouter, HTTPException

from app.models.session import SessionCreate, SessionResponse
from app.services.session import session_service

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=SessionResponse)
async def create_session(data: SessionCreate):
    """Crear nueva sesión de análisis."""
    return await session_service.create(data)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Obtener estado de una sesión."""
    try:
        return await session_service.get(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/finish", response_model=SessionResponse)
async def finish_session(session_id: str):
    """Finalizar una sesión."""
    try:
        return await session_service.finish(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))