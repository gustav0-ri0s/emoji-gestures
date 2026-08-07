"""Punto de entrada de la aplicacion emoji-gestures.

FASE 8 (final): estabilizacion temporal + resolucion de prioridad via
GestureManager, e interfaz final. Pipeline completo: camara -> deteccion
facial/manos -> clasificacion de gestos -> estabilizacion -> render de
emoji sobre el frame.
"""
import time

import cv2

import config
from camera import Camera
from combined_gestures import classify_combined_gestures
from emoji_renderer import EmojiRenderer
from face_detector import FaceDetector
from face_gestures import classify_face_gestures
from gesture_manager import GestureManager
from hand_detector import HandDetector
from hand_gestures import classify_hand_gestures


def main():
    debug = config.DEBUG
    show_landmarks = config.SHOW_LANDMARKS

    face_detector = FaceDetector()
    hand_detector = HandDetector()
    emoji_renderer = EmojiRenderer()
    gesture_manager = GestureManager()

    with Camera() as camera:
        prev_time = time.time()
        fps = 0.0

        while True:
            frame = camera.read()
            if frame is None:
                print("No se pudo leer un frame de la camara. Saliendo.")
                break

            now = time.time()
            dt = now - prev_time
            prev_time = now
            if dt > 0:
                # Suavizado simple para que el numero no salte demasiado.
                fps = fps * 0.9 + (1.0 / dt) * 0.1

            face_landmarks = face_detector.process(frame)

            face_candidates = set()
            face_metrics = None
            if face_landmarks is not None:
                face_candidates, face_metrics = classify_face_gestures(face_landmarks)

            hand_landmarks = hand_detector.process(frame)

            hand_candidates = set()
            hand_debug = None
            if hand_landmarks is not None:
                hand_candidates, hand_debug = classify_hand_gestures(hand_landmarks)

            combined_candidates, combined_debug = classify_combined_gestures(
                face_landmarks, hand_landmarks
            )

            if show_landmarks and face_landmarks is not None:
                face_detector.draw(frame, face_landmarks)

            if show_landmarks and hand_landmarks is not None:
                hand_detector.draw(frame, hand_landmarks)

            if debug:
                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"DEBUG ON (D)   Landmarks: {'ON' if show_landmarks else 'OFF'} (L)",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"Rostro detectado: {'SI' if face_landmarks is not None else 'NO'}",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

                if face_metrics is not None:
                    debug_lines = [
                        f"EAR der: {face_metrics['ear_right']:.3f}  EAR izq: {face_metrics['ear_left']:.3f}",
                        f"Apertura boca: {face_metrics['mouth_open_ratio']:.3f}",
                        f"Smile ratio: {face_metrics['smile_ratio']:.3f}",
                        f"Candidatos rostro: {', '.join(sorted(face_candidates)) or '--'}",
                    ]
                    for i, line in enumerate(debug_lines):
                        cv2.putText(
                            frame,
                            line,
                            (10, 120 + i * 25),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (0, 255, 255),
                            1,
                        )

                cv2.putText(
                    frame,
                    f"Mano detectada: {'SI' if hand_landmarks is not None else 'NO'}",
                    (10, 220),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

                if hand_debug is not None:
                    extended = [
                        name for name, is_ext in hand_debug["states"].items() if is_ext
                    ]
                    cv2.putText(
                        frame,
                        f"Dedos extendidos: {', '.join(extended) or '--'}",
                        (10, 250),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 255),
                        1,
                    )
                    ratios_txt = "  ".join(
                        f"{name}:{ratio:.2f}" for name, ratio in hand_debug["ratios"].items()
                    )
                    cv2.putText(
                        frame,
                        ratios_txt,
                        (10, 275),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 200, 200),
                        1,
                    )
                    cv2.putText(
                        frame,
                        f"Angulo pulgar: {hand_debug['thumb_angle']:.1f}  Candidatos mano: {', '.join(sorted(hand_candidates)) or '--'}",
                        (10, 300),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 255),
                        1,
                    )

                thinking_dist = combined_debug.get("thinking_distance")
                thinking_txt = (
                    f"{thinking_dist:.3f}" if thinking_dist is not None else "--"
                )
                cv2.putText(
                    frame,
                    f"Distancia pensando: {thinking_txt}  Candidatos combinados: {', '.join(sorted(combined_candidates)) or '--'}",
                    (10, 325),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 255),
                    1,
                )

            all_candidates = face_candidates | hand_candidates | combined_candidates
            active_gesture = gesture_manager.update(all_candidates)

            if active_gesture is not None:
                emoji_renderer.overlay(frame, active_gesture)

            if debug:
                stab = gesture_manager.debug_info()
                cv2.putText(
                    frame,
                    f"Candidato: {stab['candidate'] or '--'}  Confirmado: {stab['confirmed'] or '--'}  Confianza: {stab['confidence']:.2f}",
                    (10, 350),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 255),
                    1,
                )

            gesto_texto = active_gesture.upper() if active_gesture else "--"
            cv2.putText(
                frame,
                f"GESTO: {gesto_texto}",
                (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.imshow(config.WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:  # 27 = ESC
                break
            elif key == ord("d"):
                debug = not debug
            elif key == ord("l"):
                show_landmarks = not show_landmarks

    face_detector.close()
    hand_detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
