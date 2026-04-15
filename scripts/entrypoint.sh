#!/bin/bash
set -e

echo "Iniciando ExpoLens..."

# Verificar y descargar modelos
bash /code/scripts/download_models.sh

# Ejecutar el comando del contenedor
exec "$@"