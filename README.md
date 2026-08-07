# Emoji Gestures

Reconocimiento en tiempo real de gestos faciales y de mano con la webcam,
usando MediaPipe + OpenCV y reglas geometricas sobre landmarks (sin
entrenar ningun modelo). Al detectar un gesto, se muestra el PNG
correspondiente superpuesto sobre el video.

<img width="60%" height="60%" alt="image" src="https://github.com/user-attachments/assets/3f46bb83-93da-4bfa-a295-3d5e433968c1" />


## Gestos soportados

| Gesto | Emoji | Archivo |
|---|---|---|
| Dormir (ambos ojos cerrados) | 😴 | `dormir.png` |
| Guino (cualquier ojo) | 😉 | `guino.png` |
| Indice levantado | ☝️ | `indice.png` |
| Pensando (rostro + mano) | 🤔 | `pensando.png` |
| Pulgar abajo | 👎 | `pulgar_abajo.png` |
| Pulgar arriba | 👍 | `pulgar_arriba.png` |
| Puno cerrado | 👊 | `puno.png` |
| Sonrisa | 😄 | `sonrisa.png` |
| Sorpresa (boca abierta) | 😮 | `sorpresa.png` |

## Requisitos

Versiones base del entorno (ver `requirements.txt`, NO actualizar):

```
Python 3.10.9
mediapipe==0.10.9
opencv-python==4.11.0.86
numpy==1.26.4
```

Instalar dependencias (si aun no estan instaladas):

```
pip install -r requirements.txt
```

## Ejecutar

```
python src/main.py
```

## Controles

| Tecla | Accion |
|---|---|
| `Q` o `ESC` | Cerrar la aplicacion |
| `D` | Activar/desactivar texto de DEBUG (FPS, metricas, candidatos, etc.) |
| `L` | Activar/desactivar el dibujo de la malla de landmarks (rostro/mano) |

## Estructura del proyecto

```
assets/emojis/       PNG de cada gesto (con transparencia)
src/
  config.py           Configuracion centralizada: thresholds, prioridad, estabilizacion
  camera.py           Captura de video
  face_detector.py    Wrapper de MediaPipe Face Mesh
  hand_detector.py     Wrapper de MediaPipe Hands
  face_gestures.py     Reglas geometricas: guino, sonrisa, sorpresa
  hand_gestures.py     Reglas geometricas: indice, pulgar arriba/abajo, puno
  combined_gestures.py Gesto "pensando" (rostro + mano)
  gesture_manager.py   Prioridad + estabilizacion temporal
  emoji_renderer.py    Carga/cache y overlay de los PNG
  main.py              Loop principal
```

## Calibracion

Todos los thresholds de deteccion viven en `src/config.py` y fueron
calibrados con datos reales de camara (ver comentarios en el archivo).
Si los gestos no se detectan bien con otra camara o iluminacion,
activa `D` para ver las metricas en vivo (EAR, aperturas, ratios de
dedos, angulo de pulgar, distancia de "pensando") y ajusta los
valores correspondientes en `config.py`.
