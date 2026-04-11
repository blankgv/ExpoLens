# ExpoLens

Motor de diagnóstico inteligente para retroalimentación y evaluación de presentaciones orales.

## ¿Qué es?

ExpoLens es un módulo backend autónomo que analiza en tiempo real video y audio de un presentador durante una presentación oral. Detecta:

- **Palabras de relleno** ("este", "o sea", "vale", "em"...)
- **Problemas de postura** (hombros caídos, inclinación, rigidez)
- **Falta de contacto visual** (mirada perdida, leer demasiado)
- **Gestos repetitivos** (manos en bolsillos, frotarse las manos)
- **Signos de nerviosismo** (tics faciales, movimientos excesivos)
- **Ritmo de habla** (muy rápido o muy lento)

Entrega feedback constructivo en tiempo real para que el presentador mejore.

## Stack

- **FastAPI** — API REST + WebSocket
- **MediaPipe** — Análisis de pose y expresiones faciales
- **faster-whisper** — Transcripción de voz en tiempo real
- **Mistral/Llama** — Generación de feedback con LLM
- **Docker** — Containerización completa

## Requisitos

- Docker y Docker Compose

## Instalación

```bash
git clone <tu-repo>
cd expolens
cp .env.example .env
docker compose up --build
```

## Uso

La API se consume desde la aplicación principal mediante endpoints REST y WebSocket.

**Base URL:** `http://localhost:8000`
**Documentación interactiva:** `http://localhost:8000/docs`

Todas las peticiones requieren el header `X-API-Key`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/sessions` | Crear sesión de análisis |
| `GET` | `/api/v1/sessions/{id}` | Estado de una sesión |
| `POST` | `/api/v1/sessions/{id}/finish` | Finalizar sesión |
| `GET` | `/api/v1/sessions/{id}/metrics` | Métricas acumuladas |
| `GET` | `/api/v1/sessions/{id}/report` | Reporte final |
| `WS` | `/api/v1/stream/{id}` | Stream video+audio en tiempo real |

## Licencia

Privado — Todos los derechos reservados.