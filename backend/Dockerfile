FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    HF_HOME=/home/legalmind/.cache/huggingface \
    TOKENIZERS_PARALLELISM=false \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first, so this large layer stays cached
# when requirements.txt changes.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
    torch==2.15.0 \
    torchvision==0.29.2 \
    --index-url https://download.pytorch.org/whl/cpu

# Python dependencies (copied after torch on purpose)
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

RUN pip check

RUN python -c "import torch; import torchvision; import email_validator; from transformers import PreTrainedModel; from sentence_transformers import SentenceTransformer; print('ML dependencies verified successfully')"

# Create non-root application user
RUN useradd --create-home legalmind

RUN mkdir -p /home/legalmind/.cache/huggingface \
    && chown -R legalmind:legalmind /home/legalmind/.cache

# Application source
COPY --chown=legalmind:legalmind database/ ./database/
COPY --chown=legalmind:legalmind services/ ./services/
COPY --chown=legalmind:legalmind rag/ ./rag/
COPY --chown=legalmind:legalmind workers/ ./workers/
COPY --chown=legalmind:legalmind api/ ./api/
COPY --chown=legalmind:legalmind main.py .

USER legalmind

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=3)"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]