import os
from pathlib import Path
from statistics import mean

import cv2
import numpy as np
import pytesseract

from PIL import Image, ImageOps
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader


class ImageLoader(BaseLoader):

    SUPPORTED_FORMATS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tif",
        ".tiff",
        ".bmp",
    }

    def __init__(
        self,
        file_path: str,
        languages: str = "hin+eng",
        config: str = "--oem 3 --psm 6",
        tesseract_path: str | None = None,
    ):
        self.file_path = Path(file_path)
        self.languages = languages
        self.config = config

        # Resolve Tesseract executable path.
        tesseract_path = (
            tesseract_path or os.getenv("TESSERACT_CMD")
        )

        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Image not found: {self.file_path}"
            )

        if self.file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {self.file_path.suffix}"
            )

        print(f"OCR configuration: {self.config}")

    # --------------------------------------------------
    # BASELINE PREPROCESSING
    # --------------------------------------------------

    def _preprocess_image(
        self,
        image: Image.Image
    ) -> Image.Image:
        """
        Baseline preprocessing:
        EXIF correction -> grayscale -> autocontrast -> resize.
        """

        image = ImageOps.exif_transpose(image)
        image = image.convert("L")
        image = ImageOps.autocontrast(image)

        if image.width < 1600:
            scale = 1600 / image.width

            new_size = (
                1600,
                int(image.height * scale)
            )

            image = image.resize(
                new_size,
                Image.Resampling.LANCZOS
            )

        return image

    # --------------------------------------------------
    # OPENCV PREPROCESSING EXPERIMENTS
    # --------------------------------------------------

    def _preprocess_opencv(
        self,
        image: Image.Image,
        method: str
    ) -> Image.Image:
        """
        OpenCV preprocessing variants:

        otsu:
            Automatic global thresholding.

        adaptive:
            Local adaptive thresholding.

        denoise_otsu:
            Noise reduction followed by Otsu thresholding.
        """

        image = ImageOps.exif_transpose(image)
        image = image.convert("L")

        # Resize small images.
        if image.width < 1600:
            scale = 1600 / image.width

            new_size = (
                1600,
                int(image.height * scale)
            )

            image = image.resize(
                new_size,
                Image.Resampling.LANCZOS
            )

        image_array = np.array(image)

        if method == "otsu":

            _, processed = cv2.threshold(
                image_array,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

        elif method == "adaptive":

            processed = cv2.adaptiveThreshold(
                image_array,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                11
            )

        elif method == "denoise_otsu":

            denoised = cv2.fastNlMeansDenoising(
                image_array,
                None,
                10,
                7,
                21
            )

            _, processed = cv2.threshold(
                denoised,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

        else:
            raise ValueError(
                f"Unknown preprocessing method: {method}"
            )

        return Image.fromarray(processed)
    
    def _deskew(self, image_array: np.ndarray) -> np.ndarray:
        """
        Correct small rotation angles using foreground pixels.
        Assumes dark text on a light background.
        """

        binary = cv2.threshold(
            image_array,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        coords = np.column_stack(np.where(binary > 0))

        if len(coords) < 100:
            return image_array

        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Avoid aggressive or unreliable rotations.
        if abs(angle) > 5:
            return image_array

        if abs(angle) < 0.1:
            return image_array

        height, width = image_array.shape

        center = (width // 2, height // 2)

        matrix = cv2.getRotationMatrix2D(
            center,
            angle,
            1.0
        )

        rotated = cv2.warpAffine(
            image_array,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=255
        )

        return rotated

    def _preprocess_advanced(
        self,
        image: Image.Image,
        method: str
    ) -> Image.Image:
        """
        Advanced preprocessing experiments:

        deskew
        clahe
        sharpen
        combined
        """

        image = ImageOps.exif_transpose(image)
        image = image.convert("L")

        if image.width < 1600:
            scale = 1600 / image.width

            image = image.resize(
                (
                    1600,
                    int(image.height * scale)
                ),
                Image.Resampling.LANCZOS
            )

        image_array = np.array(image)

        if method == "deskew":
            processed = self._deskew(image_array)

        elif method == "clahe":
            clahe = cv2.createCLAHE(
                clipLimit=2.0,
                tileGridSize=(8, 8)
            )

            processed = clahe.apply(image_array)

        elif method == "sharpen":
            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ], dtype=np.float32)

            processed = cv2.filter2D(
                image_array,
                -1,
                kernel
            )

        elif method == "combined":
            processed = self._deskew(image_array)

            clahe = cv2.createCLAHE(
                clipLimit=2.0,
                tileGridSize=(8, 8)
            )

            processed = clahe.apply(processed)

            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ], dtype=np.float32)

            processed = cv2.filter2D(
                processed,
                -1,
                kernel
            )

        else:
            raise ValueError(
                f"Unknown advanced preprocessing method: {method}"
            )

        return Image.fromarray(processed)


    # --------------------------------------------------
    # OCR EXTRACTION
    # --------------------------------------------------

    def _extract_ocr(
        self,
        image: Image.Image
    ) -> tuple[str, float | None]:
        """
        Extract OCR text and calculate average word confidence.

        Note:
        Tesseract confidence is not equivalent to actual
        transcription accuracy.
        """

        text = pytesseract.image_to_string(
            image,
            lang=self.languages,
            config=self.config
        )

        ocr_data = pytesseract.image_to_data(
            image,
            lang=self.languages,
            config=self.config,
            output_type=pytesseract.Output.DICT
        )

        confidence_scores = []

        for confidence in ocr_data["conf"]:

            try:
                confidence = float(confidence)

                if confidence >= 0:
                    confidence_scores.append(confidence)

            except (ValueError, TypeError):
                continue

        average_confidence = (
            round(mean(confidence_scores), 2)
            if confidence_scores
            else None
        )

        return text.strip(), average_confidence

    # --------------------------------------------------
    # LANGCHAIN DOCUMENT LOADER
    # --------------------------------------------------

    def lazy_load(self):
        """
        LangChain-compatible document loader.
        """

        with Image.open(self.file_path) as original_image:

            image = self._preprocess_image(original_image)

            text, confidence = self._extract_ocr(image)

        if not text:
            raise ValueError(
                "No text detected in image. "
                "Check image quality or orientation."
            )

        yield Document(
            page_content=text,
            metadata={
                "source": str(self.file_path),
                "page_number": 1,
                "file_type": "image",
                "ocr_language": self.languages,
                "ocr_confidence": confidence,
            }
        )

    # --------------------------------------------------
    # LEGALMIND PIPELINE ADAPTER
    # --------------------------------------------------

    def load_pages(self) -> list[dict]:
        """
        Converts LangChain Documents into the page format
        expected by normalize_text() and chunk_pages().
        """

        documents = self.load()

        return [
            {
                "page_number": document.metadata["page_number"],
                "text": document.page_content,
                "metadata": document.metadata,
            }
            for document in documents
        ]
    
    def run_ocr(self, method: str = "baseline"):
        """
        Run OCR using a selected preprocessing method.

        This method is intended for benchmarking.
        Production lazy_load() continues to use baseline preprocessing.
        """

        opencv_methods = {
            "otsu",
            "adaptive",
            "denoise_otsu",
        }

        advanced_methods = {
            "deskew",
            "clahe",
            "sharpen",
            "combined",
        }

        with Image.open(self.file_path) as original:
            image = original.copy()

        if method == "baseline":
            processed = self._preprocess_image(image)

        elif method in opencv_methods:
            processed = self._preprocess_opencv(
                image,
                method
            )

        elif method in advanced_methods:
            processed = self._preprocess_advanced(
                image,
                method
            )

        else:
            raise ValueError(
                f"Unsupported preprocessing method: {method}"
            )

        text, confidence = self._extract_ocr(processed)

        if not text.strip():
            raise ValueError(
                f"OCR produced no text using method: {method}"
            )

        return text, confidence

