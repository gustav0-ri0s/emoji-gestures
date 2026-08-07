"""Deteccion de manos y landmarks usando MediaPipe Hands."""
import cv2
import mediapipe as mp

import config

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class HandDetector:
    """Envuelve mediapipe.solutions.hands y expone landmarks normalizados."""

    def __init__(self):
        self._hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.HAND_MAX_NUM_HANDS,
            min_detection_confidence=config.HAND_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.HAND_MIN_TRACKING_CONFIDENCE,
        )

    def process(self, frame_bgr):
        """Devuelve el NormalizedLandmarkList de la primera mano detectada
        (landmarks accesibles via .landmark[i].x/.y/.z), o None si no se
        detecto ninguna mano."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)

        if not results.multi_hand_landmarks:
            return None

        return results.multi_hand_landmarks[0]

    def draw(self, frame_bgr, hand_landmarks_proto):
        mp_drawing.draw_landmarks(
            image=frame_bgr,
            landmark_list=hand_landmarks_proto,
            connections=mp_hands.HAND_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
            connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
        )

    def close(self):
        self._hands.close()
