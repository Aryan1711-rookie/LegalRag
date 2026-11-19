import re

from html import unescape
from threading import Lock

from PIL import Image

from surya.inference import SuryaInferenceManager
from surya.recognition import RecognitionPredictor

from app.schemas import OCRBlock, OCRPage
from app.preprocessing.image_preprocessor import ImagePreprocessor

from app.config import (
    OCR_ADAPTIVE_UPSCALE,
    OCR_MAX_IMAGE_DIMENSION,
)

class SuryaEngine:

    def __init__(self):

        self.manager = SuryaInferenceManager()

        self.predictor = RecognitionPredictor(
            self.manager
        )
        self.preprocessor = ImagePreprocessor(
        enabled=OCR_ADAPTIVE_UPSCALE,
        max_dimension=OCR_MAX_IMAGE_DIMENSION,
        )

        self._lock = Lock()

    @staticmethod
    def html_to_text(html: str) -> str:

        html = re.sub(
            r"<br\s*/?>",
            "\n",
            html,
            flags=re.I
        )

        html = re.sub(
            r"</(?:td|th)>",
            " ",
            html,
            flags=re.I
        )

        html = re.sub(
            r"</(?:p|tr|div|li)>",
            "\n",
            html,
            flags=re.I
        )

        text = re.sub(r"<[^>]+>", "", html)

        return unescape(text).strip()

    def extract(self, image: Image.Image) -> OCRPage:

        image, preprocessing = (
            self.preprocessor.preprocess(image)
        )

        with self._lock:

            predictions = self.predictor(
                [image],
                full_page=True,
            )

        if not predictions:

            raise RuntimeError(
                "Surya returned no predictions."
            )

        result = predictions[0].model_dump()

        blocks = []
        paragraphs = []

        scale_x = (
            preprocessing["processed_width"]
            / preprocessing["original_width"]
        )

        scale_y = (
            preprocessing["processed_height"]
            / preprocessing["original_height"]
        )

        def restore_bbox(bbox):

            return [
                round(bbox[0] / scale_x, 4),
                round(bbox[1] / scale_y, 4),
                round(bbox[2] / scale_x, 4),
                round(bbox[3] / scale_y, 4),
            ]

        raw_blocks = sorted(
            result["blocks"],
            key=lambda block: block["reading_order"]
        )

        for block in raw_blocks:

            html = block.get("html") or ""

            text = self.html_to_text(html)

            skipped = block.get("skipped", False)
            error = block.get("error", False)

            blocks.append(
                OCRBlock(
                    label=block["label"],
                    reading_order=block["reading_order"],
                    bbox=restore_bbox(block["bbox"]),
                    html=html,
                    text=text,
                    confidence=block.get("confidence"),
                    skipped=skipped,
                    error=error,
                )
            )

            if text and not skipped and not error:

                paragraphs.append(text)

        return OCRPage(
            page_number=1,
            image_bbox=restore_bbox(
                result["image_bbox"]
            ),
            text="\n\n".join(paragraphs),
            blocks=blocks,
            preprocessing=preprocessing,
        )