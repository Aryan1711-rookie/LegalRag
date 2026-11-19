import os
import logging

import pymupdf

from rag.ingestion.classifiers.pdf_classifier import (
    PDFClassifier
)

from rag.ingestion.clients.ocr_client import (
    OCRClient
)


logger = logging.getLogger(__name__)


def extract_text(pdf_path: str):

    classifier = PDFClassifier()

    ocr_client = None

    extracted_pages = []

    render_dpi = int(
        os.getenv("OCR_RENDER_DPI", "192")
    )

    try:

        with pymupdf.open(pdf_path) as doc:

            total_pages = len(doc)

            for page_num, page in enumerate(doc):

                page_number = page_num + 1

                native_text = page.get_text(
                    "text",
                    sort=True,
                )

                classification = classifier.classify_page(
                    page,
                    native_text,
                )

                page_type = classification["page_type"]

                logger.info(
                    "Page %s/%s classified as %s",
                    page_number,
                    total_pages,
                    page_type,
                )

                # Blank page
                if page_type == "blank":

                    extracted_pages.append({
                        "page_number": page_number,
                        "text": "",
                        "page_type": "blank",
                        "extraction_method": "none",
                        "metadata": classification,
                    })

                    continue

                # Digital text extraction
                if not classification["requires_ocr"]:

                    extracted_pages.append({
                        "page_number": page_number,
                        "text": native_text,
                        "page_type": page_type,
                        "extraction_method": "pymupdf",
                        "metadata": classification,
                    })

                    continue

                # Initialize OCR client only when needed
                if ocr_client is None:

                    ocr_client = OCRClient()

                # Render scanned or hybrid page
                pixmap = page.get_pixmap(
                    dpi=render_dpi,
                    alpha=False,
                )

                image_bytes = pixmap.tobytes("png")

                logger.info(
                    "Sending page %s to OCR service",
                    page_number,
                )

                ocr_result = ocr_client.extract(
                    image_bytes=image_bytes,
                    filename=f"page_{page_number}.png",
                )

                extracted_pages.append({
                    "page_number": page_number,
                    "text": ocr_result["text"],
                    "page_type": page_type,
                    "extraction_method": "surya",
                    "native_text": native_text,
                    "blocks": ocr_result["blocks"],
                    "metadata": {
                        **classification,
                        "ocr_engine": ocr_result["engine"],
                        "ocr_model": ocr_result["model"],
                        "ocr_time_seconds": ocr_result[
                            "execution_time_seconds"
                        ],
                        "preprocessing": ocr_result[
                            "preprocessing"
                        ],
                        "render_dpi": render_dpi,
                        "image_bbox": ocr_result["image_bbox"],
                    },
                })

    finally:

        if ocr_client is not None:

            ocr_client.close()

    return extracted_pages