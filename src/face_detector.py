"""Deteccion facial y landmarks usando MediaPipe Face Mesh."""
import cv2
import mediapipe as mp

import config

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class FaceDetector:
    """Envuelve mediapipe.solutions.face_mesh y expone landmarks normalizados."""

    def __init__(self):
        self._face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=config.FACE_MAX_NUM_FACES,
            refine_landmarks=True,  # incluye landmarks de iris, mejora ojos/labios
            min_detection_confidence=config.FACE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.FACE_MIN_TRACKING_CONFIDENCE,
        )

    def process(self, frame_bgr):
        """Devuelve el NormalizedLandmarkList del primer rostro detectado
        (landmarks accesibles via .landmark[i].x/.y/.z), o None si no se
        detecto ningun rostro."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        return results.multi_face_landmarks[0]

    def draw(self, frame_bgr, landmarks_proto):
        """Dibuja la malla facial completa sobre el frame (uso en DEBUG)."""
        mp_drawing.draw_landmarks(
            image=frame_bgr,
            landmark_list=landmarks_proto,
            connections=mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
        )
        mp_drawing.draw_landmarks(
            image=frame_bgr,
            landmark_list=landmarks_proto,
            connections=mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style(),
        )

    def close(self):
        self._face_mesh.close()
