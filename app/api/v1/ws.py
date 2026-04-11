from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["streaming"])


@router.websocket("/stream/{session_id}")
async def stream(websocket: WebSocket, session_id: str):
    """CU-02: Stream de video+audio en tiempo real."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"echo": data, "session_id": session_id})
    except WebSocketDisconnect:
        pass
