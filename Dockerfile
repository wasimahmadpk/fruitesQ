# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps for Pillow / torch
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Runtime system deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy source
COPY src/ src/
COPY mlflow_tracking.py .

# Hugging Face cache persisted as a volume in production
ENV HF_HOME=/app/.cache/huggingface
ENV MLFLOW_TRACKING_URI=mlruns
ENV PYTHONUNBUFFERED=1

# Expose API port and Streamlit port
EXPOSE 8000 8501

# Default: start FastAPI.  Override CMD to run Streamlit instead.
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
