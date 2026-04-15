import numpy as np
import cv2

from app.pipelines.video import VideoPipeline


def test_process_empty_frame():
    """Frame inválido devuelve métricas por defecto."""
    pipeline = VideoPipeline()
    result = pipeline.process_frame(b"datos invalidos")

    assert isinstance(result["posture"], object)
    assert isinstance(result["gestures"].movement_level, str)
    assert isinstance(result["face"].eye_contact_pct, float)
    pipeline.release()


def test_process_black_frame():
    """Frame negro sin persona devuelve score bajo."""
    pipeline = VideoPipeline()

    black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", black_frame)
    frame_bytes = encoded.tobytes()

    result = pipeline.process_frame(frame_bytes)

    assert result["posture"].score == 0.0
    assert "no se detectó persona" in result["posture"].issues
    pipeline.release()