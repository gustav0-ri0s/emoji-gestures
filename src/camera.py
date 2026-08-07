"""Manejo de la captura de video de la webcam."""
import cv2

import config


class Camera:
    """Wrapper simple sobre cv2.VideoCapture."""

    def __init__(self, index=None, width=None, height=None):
        self.index = config.CAMERA_INDEX if index is None else index
        self.width = config.CAMERA_WIDTH if width is None else width
        self.height = config.CAMERA_HEIGHT if height is None else height
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            # Reintento sin backend explicito por si CAP_DSHOW falla.
            self.cap = cv2.VideoCapture(self.index)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"No se pudo abrir la camara con indice {self.index}."
            )

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return self

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return cv2.flip(frame, 1)  # efecto espejo, mas natural para el usuario

    def release(self):
        if self.cap is not None:
            self.cap.release()

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
