# Stage 1: Build the frontend
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source files
COPY frontend/ ./

# Build the frontend (outputs to ../static which is /static in this context)
RUN npm run build


# Stage 2: Build the final image with Python backend
FROM python:3.12-slim

# Prevent Python from buffering logs (crucial for seeing errors in Cloud Run)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (Cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app/ ./app/

# Copy the built frontend from the frontend builder stage
COPY --from=frontend-builder /static ./static/

# Security: Run as non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set PYTHONPATH so 'uvicorn' can find the 'app' module
ENV PYTHONPATH=/app

# The Start Command
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
