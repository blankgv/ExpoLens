FROM python:3.11-slim

WORKDIR /code

# Instalar uv (gestor de paquetes de Python, más rápido que pip)
RUN pip install uv

# Copiar archivo de dependencias
COPY pyproject.toml .

# Instalar dependencias (FastAPI, uvicorn, pydantic, redis)
RUN uv pip install --system -e ".[dev]"

# Copiar el código de la app
COPY app/ app/
COPY tests/ tests/

EXPOSE 8000

# Comando que arranca el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
