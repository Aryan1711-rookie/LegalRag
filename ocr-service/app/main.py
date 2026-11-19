import logging
import time

from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path

import httpx

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request,
)

from PIL import Image, ImageOps, UnidentifiedImageError

# Load configuration before importing Surya.
from app.config import (
    OCR_MAX_FILE_SIZE,
    SURYA_INFERENCE_URL,
)

from app.engines.surya_engine import SuryaEngine
from app.schemas import OCRResponse


logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}

MAX_IMAGE_PIXELS = 25_000_000


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.ocr_engine = SuryaEngine()

    yield


app = FastAPI(
    title="LegalMind OCR Service",
    description="Structured Hindi and English OCR",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "legalmind-ocr"
    }


@app.get("/ready")
def ready():

    health_url = (
        SURYA_INFERENCE_URL.rstrip("/")
        .removesuffix("/v1")
        + "/health"
    )

    try:

        response = httpx.get(
            health_url,
            timeout=5.0
        )

        response.raise_for_status()

    except httpx.HTTPError:

        raise HTTPException(
            status_code=503,
            detail="OCR inference server unavailable."
        )

    return {
        "status": "ready",
        "engine": "surya"
    }


@app.post("/ocr", response_model=OCRResponse)
def extract_ocr(
    request: Request,
    file: UploadFile = File(...)
):

    filename = file.filename or "image"

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG and PNG are supported."
        )

    content = file.file.read(
        OCR_MAX_FILE_SIZE + 1
    )

    if len(content) > OCR_MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail="File exceeds maximum upload size."
        )

    try:

        with Image.open(BytesIO(content)) as source:

            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="Image resolution is too large."
                )

            image = ImageOps.exif_transpose(
                source
            ).convert("RGB")

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        OSError
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image."
        )

    start_time = time.perf_counter()

    try:

        engine = request.app.state.ocr_engine

        page = engine.extract(image)

    except Exception:

        logger.exception("OCR extraction failed")

        raise HTTPException(
            status_code=502,
            detail="OCR inference failed."
        )

    execution_time = time.perf_counter() - start_time

    return OCRResponse(
        status=(
            "review_required"
            if not page.text.strip()
            or any(block.error for block in page.blocks)
            else "success"
        ),
        engine="surya",
        model="surya-2.5",
        filename=filename,
        total_pages=1,
        execution_time_seconds=round(
            execution_time,
            4
        ),
        pages=[page],
    )