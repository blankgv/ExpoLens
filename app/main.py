from fastapi import FastAPI, Depends

from app.config import settings
from app.core.security import verify_api_key
from app.api.v1.rest import router as rest_router
from app.api.v1.ws import router as ws_router

app = FastAPI(
    title=settings.app_name,
    description="Motor de diagnóstico inteligente para retroalimentación y evaluación de presentaciones orales",
    version="0.1.0",
)

app.include_router(rest_router, prefix="/api/v1", dependencies=[Depends(verify_api_key)])
app.include_router(ws_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}

