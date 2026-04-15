FROM python:3.11-slim

WORKDIR /code

# Instalar dependencias del sistema
COPY requirements.system .
RUN apt-get update && \
    xargs -a requirements.system apt-get install -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install uv

# Instalar dependencias en /opt/venv (fuera de /code para que el volumen no lo pise)
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra dev

# Agregar el venv al PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el código de la app
COPY app/ app/
COPY tests/ tests/
COPY scripts/ scripts/

# Configurar entrypoint
RUN chmod +x scripts/*.sh
ENTRYPOINT ["/code/scripts/entrypoint.sh"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]