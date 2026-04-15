#!/bin/bash
set -e

WEIGHTS_DIR="/code/weights/mediapipe"

if [ ! -f "$WEIGHTS_DIR/pose_landmarker.task" ] || [ ! -f "$WEIGHTS_DIR/face_landmarker.task" ]; then
    echo "Modelos no encontrados. Descargando..."
    mkdir -p "$WEIGHTS_DIR"

    curl -L -o "$WEIGHTS_DIR/pose_landmarker.task" \
        https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task

    curl -L -o "$WEIGHTS_DIR/face_landmarker.task" \
        https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task

    echo "Modelos descargados."
else
    echo "Modelos ya existen. Saltando descarga."
fi