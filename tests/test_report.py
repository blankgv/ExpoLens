from starlette.testclient import TestClient

from app.main import app
from app.config import settings


def test_report_empty_session():
    """Reporte de sesión sin datos."""
    client = TestClient(app)
    headers = {"x-api-key": settings.api_key}

    # Crear y finalizar sesión
    response = client.post(
        "/api/v1/sessions",
        json={"presenter_name": "Juan", "context": "defensa de grado"},
        headers=headers,
    )
    session_id = response.json()["id"]
    client.post(f"/api/v1/sessions/{session_id}/finish", headers=headers)

    # Pedir reporte
    response = client.get(f"/api/v1/sessions/{session_id}/report", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "Juan" in data["summary"]
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0


def test_report_not_found():
    """Sesión inexistente devuelve 404."""
    client = TestClient(app)
    headers = {"x-api-key": settings.api_key}

    response = client.get("/api/v1/sessions/no-existe/report", headers=headers)
    assert response.status_code == 404