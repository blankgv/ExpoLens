from fastapi import APIRouter

router = APIRouter(tags=["sessions"])


@router.post("/sessions")
async def create_session():
    """CU-01: Crear nueva sesión de análisis."""
    return {"message": "TODO: CU-01"}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """CU-01: Obtener estado de una sesión."""
    return {"message": "TODO: CU-01"}


@router.post("/sessions/{session_id}/finish")
async def finish_session(session_id: str):
    """CU-01: Finalizar una sesión."""
    return {"message": "TODO: CU-01"}


@router.get("/sessions/{session_id}/metrics")
async def get_metrics(session_id: str):
    """CU-06: Métricas acumuladas."""
    return {"message": "TODO: CU-06"}


@router.get("/sessions/{session_id}/report")
async def get_report(session_id: str):
    """CU-07: Reporte final."""
    return {"message": "TODO: CU-07"}
