import os
import httpx

from dotenv import load_dotenv
from pathlib import Path


load_dotenv(
    Path(__file__).resolve().parents[3] / ".env"
)


class OCRServiceError(RuntimeError):
    pass


class OCRClient:

    def __init__(self):

        self.base_url = os.getenv(
            "OCR_SERVICE_URL",
            "http://127.0.0.1:8001",
        ).rstrip("/")

        self.timeout = float(
            os.getenv("OCR_TIMEOUT_SECONDS", "600")
        )

        self.client = httpx.Client(
            timeout=httpx.Timeout(
                self.timeout,
                connect=10.0,
            )
        )

    def is_ready(self) -> bool:

        try:

            response = self.client.get(
                f"{self.base_url}/ready",
                timeout=5.0,
            )

            return response.status_code == 200

        except httpx.HTTPError:

            return False

    def extract(
        self,
        image_bytes: bytes,
        filename: str = "page.png",
    ) -> dict:

        try:

            response = self.client.post(
                f"{self.base_url}/ocr",
                files={
                    "file": (
                        filename,
                        image_bytes,
                        "image/png",
                    )
                },
            )

            response.raise_for_status()

            result = response.json()

        except (httpx.HTTPError, ValueError) as error:

            raise OCRServiceError(
                f"OCR request failed for {filename}"
            ) from error

        if not result.get("pages"):

            raise OCRServiceError(
                "OCR service returned no pages."
            )

        if result.get("status") != "success":

            raise OCRServiceError(
                f"OCR requires review: {filename}"
            )

        page = result["pages"][0]

        if not page.get("text", "").strip():

            raise OCRServiceError(
                f"OCR returned empty text: {filename}"
            )

        return {
            "text": page["text"],
            "blocks": page.get("blocks", []),
            "image_bbox": page.get("image_bbox"),
            "engine": result.get("engine", "surya"),
            "model": result.get("model"),
            "preprocessing": page.get("preprocessing"),
            "execution_time_seconds": result.get(
                "execution_time_seconds"
            ),
        }

    def close(self):

        self.client.close()