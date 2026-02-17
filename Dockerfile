# ── UPI Mule Detection Platform — Production Docker Image ──
# Multi-stage build for minimal attack surface

FROM python:3.11-slim AS base

# Security: non-root user
RUN groupadd -r muledetect && useradd -r -g muledetect -d /app -s /bin/bash muledetect

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY logs/ ./logs/

# Ensure logs directory is writable
RUN mkdir -p /app/logs && chown -R muledetect:muledetect /app

# Switch to non-root user
USER muledetect

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MULE_API_KEY=csic-mule-detect-2026 \
    CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
