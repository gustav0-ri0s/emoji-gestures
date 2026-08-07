"""Gestos que combinan landmarks de rostro y de mano.

FASE 6: "pensando" — se activa cuando hay rostro y mano detectados y
al menos una punta de dedo esta cerca del menton/boca. La distancia se
normaliza por la distancia interocular del rostro para no depender de
que tan cerca este el usuario de la camara.
"""
import math

import config

CHIN = 152
MOUTH_UPPER_INNER = 13
MOUTH_LOWER_INNER = 14
RIGHT_EYE_OUTER = 33
LEFT_EYE_OUTER = 263

# Puntas de los 5 dedos (pulgar, indice, medio, anular, menique).
FINGER_TIPS = [4, 8, 12, 16, 20]


def _dist_xy(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def _midpoint(a, b):
    class _P:
        pass

    p = _P()
    p.x = (a.x + b.x) / 2
    p.y = (a.y + b.y) / 2
    return p


def compute_thinking_distance(face_landmarks, hand_landmarks):
    """Distancia normalizada (por distancia interocular) entre la punta
    de dedo mas cercana y la zona menton/boca del rostro."""
    interocular = _dist_xy(
        face_landmarks.landmark[RIGHT_EYE_OUTER], face_landmarks.landmark[LEFT_EYE_OUTER]
    )
    if interocular < 1e-6:
        interocular = 1e-6

    chin = face_landmarks.landmark[CHIN]
    mouth = _midpoint(
        face_landmarks.landmark[MOUTH_UPPER_INNER], face_landmarks.landmark[MOUTH_LOWER_INNER]
    )

    min_dist = min(
        min(
            _dist_xy(hand_landmarks.landmark[tip_idx], chin),
            _dist_xy(hand_landmarks.landmark[tip_idx], mouth),
        )
        for tip_idx in FINGER_TIPS
    )

    return min_dist / interocular


def classify_combined_gestures(face_landmarks, hand_landmarks):
    """Devuelve (set_de_gestos_candidatos, debug_dict). Requiere que tanto
    el rostro como la mano hayan sido detectados en el mismo frame."""
    candidates = set()

    if face_landmarks is None or hand_landmarks is None:
        return candidates, {"thinking_distance": None}

    distance = compute_thinking_distance(face_landmarks, hand_landmarks)
    if distance < config.THINKING_DISTANCE_THRESHOLD:
        candidates.add("pensando")

    return candidates, {"thinking_distance": distance}
