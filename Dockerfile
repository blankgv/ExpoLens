FROM python:3.11-slim

WORKDIR /code

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libxext6 \
    libsm6 \
    libgles2 \
    libegl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
# Instalar uv
RUN pip install uv

# Copiar archivo de dependencias
COPY pyproject.toml .

# Instalar dependencias
RUN uv pip install --system -e ".[dev]"

# Copiar el código de la app
COPY app/ app/
COPY tests/ tests/
COPY scripts/ scripts/

# Configurar entrypoint
RUN chmod +x scripts/*.sh
ENTRYPOINT ["scripts/entrypoint.sh"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]