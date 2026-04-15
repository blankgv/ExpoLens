import pytest
from starlette.testclient import TestClient

from app.main import app
from app.config import settings


def test_websocket_no_api_key():
    """Sin API key, el WebSocket cierra la conexión."""
    client = TestClient(app)

    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/stream/fake-session"):
            pass


def test_websocket_invalid_session():
    """Con API key pero sesión inexistente, cierra la conexión."""
    client = TestClient(app)

    with pytest.raises(Exception):
        with client.websocket_connect(
            "/api/v1/stream/no-existe",
            headers={"x-api-key": settings.api_key},
        ):
            pass


def test_websocket_echo():
    """Con sesión válida, acepta la conexión."""
    client = TestClient(app)

    # Crear sesión primero
    response = client.post(
        "/api/v1/sessions",
        json={"presenter_name": "Test", "context": "prueba"},
        headers={"x-api-key": settings.api_key},
    )
    session_id = response.json()["id"]

    # Conectar al WebSocket
    with client.websocket_connect(
        f"/api/v1/stream/{session_id}",
        headers={"x-api-key": settings.api_key},
    ) as ws:
        # Enviar un chunk de audio (0x02 + texto)
        audio_data = b'\x02' + "este es una prueba este".encode("utf-8")
        ws.send_bytes(audio_data)