"""Reglas geometricas para detectar gestos faciales a partir de los
landmarks de MediaPipe Face Mesh (468 puntos + iris si refine_landmarks).

Todas las medidas se normalizan respecto a distancias faciales estables
(p.ej. distancia interocular) para no depender de la distancia a la
camara ni del tamano del rostro en pixeles.
"""
import math

import config

# Indices de landmarks (MediaPipe Face Mesh, 468 puntos).
# Ojo derecho (del sujeto): [outer_corner, upper1, upper2, inner_corner, lower2, lower1]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
# Ojo izquierdo (del sujeto): [inner_corner, upper2, upper1, outer_corner, lower1, lower2]
LEFT_EYE = [362, 385, 387, 263, 373, 380]

MOUTH_LEFT_CORNER = 61
MOUTH_RIGHT_CORNER = 291
MOUTH_UPPER_INNER = 13
MOUTH_LOWER_INNER = 14

RIGHT_EYE_OUTER = 33
LEFT_EYE_OUTER = 263


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def eye_aspect_ratio(landmarks, eye_indices):
    """EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)"""
    p1, p2, p3, p4, p5, p6 = (landmarks.landmark[i] for i in eye_indices)
    vertical = _dist(p2, p6) + _dist(p3, p5)
    horizontal = _dist(p1, p4)
    if horizontal == 0:
        return 0.0
    return vertical / (2.0 * horizontal)


def _interocular_distance(landmarks):
    return _dist(landmarks.landmark[RIGHT_EYE_OUTER], landmarks.landmark[LEFT_EYE_OUTER])


def compute_face_metrics(landmarks):
    """Calcula todas las metricas normalizadas usadas por los gestos
    faciales. Devuelve un dict usado tanto para clasificar como para
    mostrar en modo DEBUG."""
    interocular = _interocular_distance(landmarks)
    if interocular == 0:
        interocular = 1e-6

    ear_right = eye_aspect_ratio(landmarks, RIGHT_EYE)
    ear_left = eye_aspect_ratio(landmarks, LEFT_EYE)

    mouth_open = _dist(
        landmarks.landmark[MOUTH_UPPER_INNER], landmarks.landmark[MOUTH_LOWER_INNER]
    )
    mouth_open_ratio = mouth_open / interocular

    mouth_width = _dist(
        landmarks.landmark[MOUTH_LEFT_CORNER], landmarks.landmark[MOUTH_RIGHT_CORNER]
    )
    smile_ratio = mouth_width / interocular

    return {
        "ear_right": ear_right,
        "ear_left": ear_left,
        "mouth_open_ratio": mouth_open_ratio,
        "smile_ratio": smile_ratio,
        "interocular": interocular,
    }


def classify_face_gestures(landmarks):
    """Devuelve (set_de_gestos_candidatos, metrics_dict)."""
    metrics = compute_face_metrics(landmarks)
    candidates = set()

    right_closed = metrics["ear_right"] < config.EYE_CLOSED_THRESHOLD
    left_closed = metrics["ear_left"] < config.EYE_CLOSED_THRESHOLD
    right_open = metrics["ear_right"] > config.EYE_OPEN_THRESHOLD
    left_open = metrics["ear_left"] > config.EYE_OPEN_THRESHOLD

    is_wink = (right_closed and left_open) or (left_closed and right_open)
    if is_wink:
        candidates.add("guino")

    is_sleeping = right_closed and left_closed
    if is_sleeping:
        candidates.add("dormir")

    is_surprise = metrics["mouth_open_ratio"] > config.MOUTH_OPEN_THRESHOLD
    if is_surprise:
        candidates.add("sorpresa")

    # Una sonrisa requiere boca ancha pero NO muy abierta verticalmente,
    # para no confundirse con sorpresa.
    is_smile = (
        metrics["smile_ratio"] > config.SMILE_THRESHOLD
        and metrics["mouth_open_ratio"] < config.MOUTH_OPEN_THRESHOLD
    )
    if is_smile:
        candidates.add("sonrisa")

    return candidates, metrics
