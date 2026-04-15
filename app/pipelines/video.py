import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from app.models.metrics import PostureMetrics, GestureMetrics, FaceMetrics

POSE_MODEL = "/code/weights/mediapipe/pose_landmarker.task"
FACE_MODEL = "/code/weights/mediapipe/face_landmarker.task"


class VideoPipeline:
    def __init__(self):
        # Configurar PoseLandmarker
        pose_options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=POSE_MODEL),
            running_mode=vision.RunningMode.IMAGE,
        )
        self._pose = vision.PoseLandmarker.create_from_options(pose_options)

        # Configurar FaceLandmarker
        face_options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=FACE_MODEL),
            running_mode=vision.RunningMode.IMAGE,
            output_face_blendshapes=True,
            num_faces=1,
        )
        self._face = vision.FaceLandmarker.create_from_options(face_options)

        # Historial para detectar gestos repetitivos
        self._hand_positions: list[tuple[float, float]] = []
        self._max_history = 30

    def process_frame(self, frame_bytes: bytes) -> dict:
        """Procesa un frame y devuelve métricas."""
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return {
                "posture": PostureMetrics(),
                "gestures": GestureMetrics(),
                "face": FaceMetrics(),
            }

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        posture = self._analyze_posture(mp_image)
        gestures = self._analyze_gestures(mp_image)
        face = self._analyze_face(mp_image)

        return {
            "posture": posture,
            "gestures": gestures,
            "face": face,
        }

    def _analyze_posture(self, mp_image: mp.Image) -> PostureMetrics:
        """Analiza postura corporal."""
        results = self._pose.detect(mp_image)

        if not results.pose_landmarks or len(results.pose_landmarks) == 0:
            return PostureMetrics(score=0.0, issues=["no se detectó persona"])

        landmarks = results.pose_landmarks[0]
        issues = []
        score = 1.0

        # Hombros: landmarks 11 (izq) y 12 (der)
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)

        if shoulder_diff > 0.05:
            issues.append("hombros desnivelados")
            score -= 0.25

        # Inclinación del torso: hombros vs caderas (23, 24)
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        mid_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
        mid_hip_x = (left_hip.x + right_hip.x) / 2

        if abs(mid_shoulder_x - mid_hip_x) > 0.06:
            issues.append("torso inclinado")
            score -= 0.25

        # Cabeza baja: nariz (0) vs hombros
        nose = landmarks[0]
        mid_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

        if nose.y > mid_shoulder_y - 0.1:
            issues.append("cabeza muy baja")
            score -= 0.25

        return PostureMetrics(score=max(score, 0.0), issues=issues)

    def _analyze_gestures(self, mp_image: mp.Image) -> GestureMetrics:
        """Detecta gestos repetitivos y nivel de movimiento."""
        results = self._pose.detect(mp_image)

        if not results.pose_landmarks or len(results.pose_landmarks) == 0:
            return GestureMetrics()

        landmarks = results.pose_landmarks[0]

        # Muñecas: 15 (izq) y 16 (der)
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]

        avg_hand_pos = (
            (left_wrist.x + right_wrist.x) / 2,
            (left_wrist.y + right_wrist.y) / 2,
        )
        self._hand_positions.append(avg_hand_pos)
        if len(self._hand_positions) > self._max_history:
            self._hand_positions.pop(0)

        movement = "normal"
        repetitive = {}

        if len(self._hand_positions) >= 10:
            deltas = []
            for i in range(1, len(self._hand_positions)):
                dx = self._hand_positions[i][0] - self._hand_positions[i - 1][0]
                dy = self._hand_positions[i][1] - self._hand_positions[i - 1][1]
                deltas.append((dx ** 2 + dy ** 2) ** 0.5)

            avg_delta = sum(deltas) / len(deltas)

            if avg_delta < 0.005:
                movement = "bajo"
            elif avg_delta > 0.03:
                movement = "excesivo"

            hand_dist = ((left_wrist.x - right_wrist.x) ** 2 + (left_wrist.y - right_wrist.y) ** 2) ** 0.5
            if hand_dist < 0.05:
                repetitive["manos juntas/frotando"] = repetitive.get("manos juntas/frotando", 0) + 1

        return GestureMetrics(repetitive_gestures=repetitive, movement_level=movement)

    def _analyze_face(self, mp_image: mp.Image) -> FaceMetrics:
        """Analiza contacto visual y expresiones."""
        results = self._face.detect(mp_image)

        if not results.face_landmarks or len(results.face_landmarks) == 0:
            return FaceMetrics(eye_contact_pct=0.0, nervousness_score=0.5)

        face_landmarks = results.face_landmarks[0]

        # Contacto visual usando posición del iris
        left_eye_center = face_landmarks[468] if len(face_landmarks) > 468 else None
        right_eye_center = face_landmarks[473] if len(face_landmarks) > 473 else None

        eye_contact = 1.0
        tics = []

        if left_eye_center and right_eye_center:
            left_eye_outer = face_landmarks[33]
            left_eye_inner = face_landmarks[133]
            eye_width = abs(left_eye_outer.x - left_eye_inner.x)

            if eye_width > 0:
                iris_position = (left_eye_center.x - left_eye_outer.x) / eye_width
                if iris_position < 0.3 or iris_position > 0.7:
                    eye_contact = 0.3

        # Boca abierta
        upper_lip = face_landmarks[13]
        lower_lip = face_landmarks[14]
        mouth_gap = abs(upper_lip.y - lower_lip.y)

        if mouth_gap > 0.03:
            tics.append("boca abierta frecuentemente")

        # Blendshapes para nerviosismo
        nervousness = 0.0
        if results.face_blendshapes and len(results.face_blendshapes) > 0:
            blendshapes = {b.category_name: b.score for b in results.face_blendshapes[0]}
            # Parpadeo excesivo
            blink = max(blendshapes.get("eyeBlinkLeft", 0), blendshapes.get("eyeBlinkRight", 0))
            if blink > 0.5:
                nervousness += 0.3
                tics.append("parpadeo excesivo")

        if eye_contact < 0.5:
            nervousness += 0.4
        if tics:
            nervousness += 0.2

        return FaceMetrics(
            eye_contact_pct=round(eye_contact, 2),
            detected_tics=tics,
            nervousness_score=round(min(nervousness, 1.0), 2),
        )

    def release(self):
        """Libera recursos."""
        self._pose.close()
        self._face.close()