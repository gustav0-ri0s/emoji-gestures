"""Carga y renderizado de los PNG de emojis.

Los 8 PNG se cargan y redimensionan UNA sola vez al iniciar la
aplicacion y se mantienen en cache en memoria (diccionario), evitando
leer disco o redimensionar en cada frame del loop principal.
"""
import os

import cv2
import numpy as np

import config

# El nombre de cada gesto coincide exactamente con el nombre de archivo
# (sin extension) dentro de assets/emojis/.
GESTURE_FILENAMES = {
    "dormir": "dormir.png",
    "guino": "guino.png",
    "indice": "indice.png",
    "pensando": "pensando.png",
    "pulgar_abajo": "pulgar_abajo.png",
    "pulgar_arriba": "pulgar_arriba.png",
    "puno": "puno.png",
    "sonrisa": "sonrisa.png",
    "sorpresa": "sorpresa.png",
}


class EmojiRenderer:
    def __init__(self, size=None):
        self.size = config.EMOJI_DISPLAY_SIZE if size is None else size
        self._cache = {}
        self._load_all()

    def _load_all(self):
        for gesture, filename in GESTURE_FILENAMES.items():
            path = os.path.join(config.EMOJI_DIR, filename)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise FileNotFoundError(f"No se pudo cargar el emoji: {path}")

            # Asegurar 4 canales (BGRA) para poder aplicar blending por
            # alpha de forma consistente aunque el PNG original no tenga
            # transparencia.
            if img.shape[2] == 3:
                alpha = np.full(img.shape[:2], 255, dtype=img.dtype)
                img = cv2.merge([img[:, :, 0], img[:, :, 1], img[:, :, 2], alpha])

            img = cv2.resize(img, (self.size, self.size), interpolation=cv2.INTER_AREA)
            self._cache[gesture] = img

    def get(self, gesture_name):
        return self._cache.get(gesture_name)

    def overlay(self, frame, gesture_name, margin=20):
        """Dibuja el emoji correspondiente en la esquina inferior derecha
        del frame, respetando la transparencia (canal alfa)."""
        emoji_img = self.get(gesture_name)
        if emoji_img is None:
            return frame

        frame_h, frame_w = frame.shape[:2]
        h, w = emoji_img.shape[:2]

        x = frame_w - w - margin
        y = frame_h - h - margin - 40  # deja espacio para el texto "GESTO:"

        if x < 0 or y < 0 or x + w > frame_w or y + h > frame_h:
            return frame  # emoji no cabe en el frame actual, se omite

        roi = frame[y : y + h, x : x + w]
        alpha = emoji_img[:, :, 3:4].astype(np.float32) / 255.0
        emoji_rgb = emoji_img[:, :, :3].astype(np.float32)
        roi_f = roi.astype(np.float32)

        blended = emoji_rgb * alpha + roi_f * (1.0 - alpha)
        frame[y : y + h, x : x + w] = blended.astype(np.uint8)

        return frame
