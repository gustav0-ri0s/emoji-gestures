"""Reglas geometricas para detectar gestos de mano a partir de los
landmarks de MediaPipe Hands (21 puntos por mano).

FASE 4: funcion reutilizable de dedos extendidos/doblados.
FASE 5: clasificacion de gestos (indice, pulgar arriba/abajo, puno).
"""
import math

import config

WRIST = 0
THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20

# (tip, pip) por cada dedo largo (no incluye pulgar, que se trata aparte).
_LONG_FINGERS = {
    "index": (INDEX_TIP, INDEX_PIP),
    "middle": (MIDDLE_TIP, MIDDLE_PIP),
    "ring": (RING_TIP, RING_PIP),
    "pinky": (PINKY_TIP, PINKY_PIP),
}


def _dist(a, b):
    # Distancia 3D (incluye z, la profundidad relativa que estima
    # MediaPipe). Usar solo x,y falla cuando la mano rota hacia la
    # camara (p.ej. un puno "de frente"), porque la proyeccion 2D
    # aplana distancias que en 3D siguen siendo grandes o pequenas.
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def _hand_scale(landmarks):
    """Distancia muneca -> nudillo medio, usada para normalizar el resto
    de medidas y que no dependan de que tan cerca este la mano de la camara."""
    scale = _dist(landmarks.landmark[WRIST], landmarks.landmark[MIDDLE_MCP])
    return scale if scale > 1e-6 else 1e-6


def compute_finger_ratios(landmarks):
    """Devuelve un dict {nombre_dedo: ratio} con las medidas crudas
    normalizadas usadas para decidir si un dedo esta extendido. Se
    exponen tambien en modo DEBUG para poder calibrar los umbrales."""
    scale = _hand_scale(landmarks)
    wrist = landmarks.landmark[WRIST]

    ratios = {}
    for name, (tip_idx, pip_idx) in _LONG_FINGERS.items():
        tip_dist = _dist(landmarks.landmark[tip_idx], wrist)
        pip_dist = _dist(landmarks.landmark[pip_idx], wrist)
        ratios[name] = (tip_dist - pip_dist) / scale

    # El pulgar se dobla CRUZANDO la palma (no hacia la muneca), asi que
    # en vez de compararlo contra la muneca se mide su distancia directa
    # al nudillo del menique: doblado, la punta del pulgar cae cerca de
    # esa zona de la palma; extendido, se aleja claramente.
    pinky_mcp = landmarks.landmark[PINKY_MCP]
    ratios["thumb"] = _dist(landmarks.landmark[THUMB_TIP], pinky_mcp) / scale

    return ratios


def get_finger_states(landmarks):
    """Devuelve (states, ratios). states es un dict {nombre_dedo: bool}
    indicando si cada dedo esta extendido."""
    ratios = compute_finger_ratios(landmarks)

    states = {}
    for name in ("index", "middle", "ring", "pinky"):
        states[name] = ratios[name] > config.FINGER_EXTENDED_MARGIN
    states["thumb"] = ratios["thumb"] > config.THUMB_EXTENDED_THRESHOLD

    return states, ratios


def thumb_vertical_angle(landmarks):
    """Angulo (grados) del vector muneca->punta_pulgar respecto a la
    vertical de la imagen. 0 grados = apuntando hacia arriba (y decreciente),
    180 grados = apuntando hacia abajo. Se usa para diferenciar pulgar
    arriba de pulgar abajo."""
    wrist = landmarks.landmark[WRIST]
    tip = landmarks.landmark[THUMB_TIP]
    dx = tip.x - wrist.x
    dy = tip.y - wrist.y  # en coords de imagen, y crece hacia abajo
    # atan2(dx, -dy): 0 grados = vector apuntando hacia arriba (-y)
    angle = math.degrees(math.atan2(dx, -dy))
    return angle


def classify_hand_gestures(landmarks):
    """Devuelve (set_de_gestos_candidatos, debug_dict) para los gestos de
    mano definidos: indice, pulgar_arriba, pulgar_abajo, puno."""
    states, ratios = get_finger_states(landmarks)
    angle = thumb_vertical_angle(landmarks)

    four_folded = (
        not states["index"]
        and not states["middle"]
        and not states["ring"]
        and not states["pinky"]
    )

    candidates = set()

    # INDICE: solo el indice extendido, pulgar indiferente.
    if states["index"] and not states["middle"] and not states["ring"] and not states["pinky"]:
        candidates.add("indice")

    # PUNO: los 4 dedos largos doblados, el pulgar no importa.
    if four_folded:
        candidates.add("puno")

    # PULGAR ARRIBA / ABAJO: 4 dedos doblados + pulgar extendido, la
    # orientacion del pulgar decide arriba vs abajo.
    if four_folded and states["thumb"]:
        if abs(angle) < config.THUMB_VERTICAL_ANGLE_THRESHOLD:
            candidates.add("pulgar_arriba")
        elif abs(abs(angle) - 180) < config.THUMB_VERTICAL_ANGLE_THRESHOLD:
            candidates.add("pulgar_abajo")

    debug = {
        "ratios": ratios,
        "states": states,
        "thumb_angle": angle,
    }
    return candidates, debug
