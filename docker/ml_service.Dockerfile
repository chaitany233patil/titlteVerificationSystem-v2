# Lightweight Dockerfile for ml-service
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal system packages (keep image light). curl is used by healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       g++ \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage build caching
COPY ml-service/requirements.txt ./requirements.txt

# Create and activate a venv, then install dependencies into it
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the app code and env
COPY ml-service/app ./app
COPY ml-service/.env ./.env

# Create non-root user and set permissions
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Put venv bin first in PATH so the container uses the venv automatically
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

# Start the FastAPI app with uvicorn from the venv
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Lightweight healthcheck (optional)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1
