# ---------- Frontend build stage ----------
FROM node:20-alpine AS fe
WORKDIR /frontend

# Install only what we need and leverage Docker layer caching
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build

# ---------- Backend runtime stage ----------
FROM python:3.11-slim AS be
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

# OS deps often needed by pdf/image libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install backend deps FIRST (for layer cache)
COPY backend/requirements.txt ./requirements.txt

# --- IMPORTANT about heavy deps (torch etc.) ---
# If your requirements.txt includes GPU wheels or huge packages that timeout,
# pin CPU wheels or remove them if not needed INSIDE the container.
# Example for CPU only (uncomment if needed):
# RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

# Copy built frontend into FastAPI static folder
# (FastAPI mounts backend/app/static/ in main.py)
RUN mkdir -p app/static
COPY --from=fe /frontend/dist/ ./app/static/

# Expose API port
EXPOSE 8000

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
