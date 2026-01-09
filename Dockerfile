FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the app folder is copied correctly
COPY app/ ./app/

RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Cloud Run ignores EXPOSE, but it's good for documentation
EXPOSE 8080



# Use 'sh -c' to ensure the $PORT environment variable is used
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"