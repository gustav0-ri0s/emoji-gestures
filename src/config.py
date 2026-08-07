"""Configuracion centralizada del proyecto emoji-gestures.

Todos los thresholds, rutas y parametros ajustables viven aqui
para evitar numeros magicos dispersos por el resto del codigo.
"""
import os

# ---------------------------------------------------------------------------
# RUTAS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMOJI_DIR = os.path.join(BASE_DIR, "assets", "emojis")

# ---------------------------------------------------------------------------
# CAMARA
# ---------------------------------------------------------------------------
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# ---------------------------------------------------------------------------
# DEBUG
# ---------------------------------------------------------------------------
DEBUG = True

# Dibujar la malla de landmarks (rostro y mano) sobre el video. Es
# independiente de DEBUG: se activa/desactiva con su propia tecla (L)
# para poder ver el texto de metricas sin las lineas sobre la cara.
SHOW_LANDMARKS = False

# ---------------------------------------------------------------------------
# ESTABILIZACION TEMPORAL DE GESTOS
# ---------------------------------------------------------------------------
# Numero de frames consecutivos que un gesto debe mantenerse para
# ser confirmado como el gesto activo.
GESTURE_CONFIRMATION_FRAMES = 5

# Numero de frames que se tolera la ausencia/perdida del gesto activo
# antes de liberarlo (evita parpadeos por un frame mal detectado).
GESTURE_RELEASE_FRAMES = 3

# Frames de confirmacion especificos por gesto, sobreescribe
# GESTURE_CONFIRMATION_FRAMES. Necesario para gestos naturalmente
# breves como el guino (un parpadeo dura menos que 5 frames): si se
# exige el mismo umbral que gestos sostenidos (p.ej. sonrisa), el
# guino nunca acumula suficientes frames seguidos para reemplazar a
# una sonrisa que ya esta activa.
GESTURE_CONFIRMATION_FRAMES_OVERRIDE = {
    "guino": 2,
}

# ---------------------------------------------------------------------------
# PRIORIDAD DE GESTOS (de mayor a menor prioridad)
# ---------------------------------------------------------------------------
GESTURE_PRIORITY = [
    "pensando",
    "indice",
    "pulgar_arriba",
    "pulgar_abajo",
    "puno",
    "dormir",
    "guino",
    "sonrisa",
    "sorpresa",
]

# ---------------------------------------------------------------------------
# THRESHOLDS - ROSTRO
# ---------------------------------------------------------------------------
# Eye Aspect Ratio: por debajo de este valor se considera el ojo cerrado.
# Calibrado con datos reales: ojo cerrado en guino = 0.078, ojos abiertos
# en reposo = 0.415-0.450.
EYE_CLOSED_THRESHOLD = 0.22

# El otro ojo debe permanecer por encima de este valor para considerar
# que el guino es intencional (evita confundir con "ambos ojos cerrados").
# Calibrado: ojo abierto durante guino = 0.340.
EYE_OPEN_THRESHOLD = 0.30

# Apertura de boca (normalizada) a partir de la cual se considera "sorpresa".
# Calibrado: neutro = 0.007, sonrisa = 0.197, boca bien abierta = 0.440.
MOUTH_OPEN_THRESHOLD = 0.30

# Medida de sonrisa (normalizada) a partir de la cual se considera sonrisa.
# Calibrado: neutro = 0.540, sonrisa normal = 0.743.
SMILE_THRESHOLD = 0.62

# ---------------------------------------------------------------------------
# THRESHOLDS - MANOS
# ---------------------------------------------------------------------------
# Umbral (ratio normalizado por el tamano de la mano) usado por la
# funcion de dedos extendidos/doblados: un dedo se considera extendido
# cuando (dist(punta,muneca) - dist(nudillo_medio,muneca)) / escala_mano
# supera este valor. Punto de partida razonable, se calibra en FASE 4/5.
FINGER_EXTENDED_MARGIN = 0.15

# Umbral (ratio normalizado) para el pulgar: se considera extendido
# cuando dist(punta_pulgar, nudillo_menique) / escala_mano supera este
# valor. Calibrado con datos reales: mano abierta = 0.84, puno = 1.29,
# pulgar arriba = 1.57, pulgar abajo = 2.77. El umbral se fija entre
# puno (no debe contar como extendido) y pulgar arriba/abajo (si deben).
THUMB_EXTENDED_THRESHOLD = 1.43

# Angulo (grados) respecto a la vertical para decidir si el pulgar
# apunta claramente hacia arriba o hacia abajo.
THUMB_VERTICAL_ANGLE_THRESHOLD = 35

# ---------------------------------------------------------------------------
# THRESHOLD - GESTO "PENSANDO" (rostro + mano)
# ---------------------------------------------------------------------------
# Distancia normalizada (respecto a la distancia interocular) entre la
# punta de dedo mas cercana y la zona menton/boca, por debajo de la cual
# se considera "pensando". Calibrado con datos reales: dedo en el
# menton = 0.280, mano en el pecho (lejos de la cara) = 1.050.
THINKING_DISTANCE_THRESHOLD = 0.35

# ---------------------------------------------------------------------------
# MODELOS MEDIAPIPE
# ---------------------------------------------------------------------------
FACE_MAX_NUM_FACES = 1
FACE_MIN_DETECTION_CONFIDENCE = 0.5
FACE_MIN_TRACKING_CONFIDENCE = 0.5

HAND_MAX_NUM_HANDS = 1
HAND_MIN_DETECTION_CONFIDENCE = 0.6
HAND_MIN_TRACKING_CONFIDENCE = 0.5

# ---------------------------------------------------------------------------
# INTERFAZ
# ---------------------------------------------------------------------------
WINDOW_NAME = "Emoji Gestures"
EMOJI_DISPLAY_SIZE = 380  # tamano (px) del emoji mostrado en la esquina
