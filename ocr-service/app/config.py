import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

OCR_MAX_FILE_SIZE = int(os.getenv("OCR_MAX_FILE_SIZE", "20480000"))  # 20 MB

OCR_MAX_FILE_SIZE_MB = OCR_MAX_FILE_SIZE / (1024 * 1024)  # Convert bytes to MB


SURYA_INFERENCE_URL = os.getenv(
    "SURYA_INFERENCE_URL", "http://localhost:8000/inference"
)
OCR_ADAPTIVE_UPSCALE = (
    os.getenv(
        "OCR_ADAPTIVE_UPSCALE",
        "true"
    ).lower() == "true"
)

OCR_MAX_IMAGE_DIMENSION = int(
    os.getenv("OCR_MAX_IMAGE_DIMENSION", "2400")
)