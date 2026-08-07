"""Resolucion de prioridad entre gestos candidatos + estabilizacion
temporal (confirmacion y liberacion por frames consecutivos).

Reglas (ver config.py para los valores):
- Cada frame puede tener varios gestos candidatos (de rostro, mano o
  combinados). Se elige el de mayor prioridad segun GESTURE_PRIORITY.
- Un gesto candidato nuevo debe repetirse GESTURE_CONFIRMATION_FRAMES
  frames consecutivos para reemplazar al gesto activo (algunos gestos
  usan un valor distinto via GESTURE_CONFIRMATION_FRAMES_OVERRIDE).
  Mientras se acumula, el gesto activo anterior se sigue mostrando (no
  hay parpadeo a "nada" mientras se decide el cambio).
- El gesto activo solo se libera (pasa a None) si no aparece NINGUN
  candidato durante GESTURE_RELEASE_FRAMES frames consecutivos.
"""
import config


def pick_by_priority(candidates):
    """Devuelve el gesto de mayor prioridad presente en candidates segun
    config.GESTURE_PRIORITY, o None si candidates esta vacio."""
    for gesture in config.GESTURE_PRIORITY:
        if gesture in candidates:
            return gesture
    return None


def _confirmation_frames_for(gesture):
    return config.GESTURE_CONFIRMATION_FRAMES_OVERRIDE.get(
        gesture, config.GESTURE_CONFIRMATION_FRAMES
    )


class GestureManager:
    def __init__(self):
        self.active_gesture = None
        self.pending_gesture = None
        self.pending_count = 0
        self.miss_count = 0

    def update(self, all_candidates):
        """Procesa los candidatos crudos de un frame y devuelve el gesto
        activo (estabilizado) tras aplicar prioridad y estabilizacion."""
        raw = pick_by_priority(all_candidates)

        if raw == self.active_gesture:
            self.miss_count = 0
            self.pending_gesture = None
            self.pending_count = 0
            return self.active_gesture

        if raw is None:
            # Nada detectado este frame: cuenta como "perdida" del gesto
            # activo, pero se tolera unos frames antes de liberarlo.
            self.pending_gesture = None
            self.pending_count = 0
            self.miss_count += 1
            if self.miss_count >= config.GESTURE_RELEASE_FRAMES:
                self.active_gesture = None
                self.miss_count = 0
            return self.active_gesture

        # Un candidato distinto al activo esta presente este frame.
        if raw == self.pending_gesture:
            self.pending_count += 1
        else:
            self.pending_gesture = raw
            self.pending_count = 1

        if self.pending_count >= _confirmation_frames_for(raw):
            self.active_gesture = raw
            self.pending_gesture = None
            self.pending_count = 0
            self.miss_count = 0

        return self.active_gesture

    def debug_info(self):
        confidence = 0.0
        if self.pending_gesture is not None:
            required = _confirmation_frames_for(self.pending_gesture)
            confidence = min(1.0, self.pending_count / required)
        elif self.active_gesture is not None:
            confidence = 1.0

        return {
            "candidate": self.pending_gesture,
            "confirmed": self.active_gesture,
            "confidence": confidence,
        }
