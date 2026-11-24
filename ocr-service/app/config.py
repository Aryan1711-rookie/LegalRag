import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# OCR upload configuration
OCR_MAX_FILE_SIZE_MB = int(
    os.getenv("OCR_MAX_FILE_SIZE_MB", "20")
)

OCR_MAX_FILE_SIZE = OCR_MAX_FILE_SIZE_MB * 1024 * 1024


# Inference configuration
SURYA_INFERENCE_URL = os.getenv(
    "SURYA_INFERENCE_URL",
    "http://127.0.0.1:8080"
)


# Image preprocessing configuration
OCR_ADAPTIVE_UPSCALE = (
    os.getenv("OCR_ADAPTIVE_UPSCALE", "true").lower() == "true"
)

OCR_MAX_IMAGE_DIMENSION = int(
    os.getenv("OCR_MAX_IMAGE_DIMENSION", "2400")
)