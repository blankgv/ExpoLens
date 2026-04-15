from starlette.testclient import TestClient

from app.main import app
from app.config import settings


def test_get_metrics_empty():
    """Sesión sin datos devuelve métricas vacías."""
    client = TestClient(app)
    headers = {"x-api-key": settings.api_key}

    # Crear sesión
    response = client.post(
        "/api/v1/sessions",
        json={"presenter_name": "Test", "context": "prueba"},
        headers=headers,
    )
    session_id = response.json()["id"]

    # Consultar métricas
    response = client.get(f"/api/v1/sessions/{session_id}/metrics", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["total_windows"] == 0
    assert data["metrics"] == []


def test_get_metrics_not_found():
    """Sesión inexistente devuelve 404."""
    client = TestClient(app)
    headers = {"x-api-key": settings.api_key}

    response = client.get("/api/v1/sessions/no-existe/metrics", headers=headers)
    assert response.status_code == 404