import pymupdf


class PDFClassifier:

    MIN_TEXT_CHARS = 50
    LARGE_IMAGE_THRESHOLD = 0.40
    MAX_INVALID_CHAR_RATIO = 0.05

    def classify_page(
        self,
        page: pymupdf.Page,
        text: str,
    ) -> dict:

        char_count = sum(
            not char.isspace()
            for char in text
        )

        invalid_ratio = (
            text.count("\ufffd") / max(char_count, 1)
        )

        image_coverage = self._image_coverage(page)

        usable_text = (
            char_count > 0
            and invalid_ratio <= self.MAX_INVALID_CHAR_RATIO
        )

        if image_coverage >= self.LARGE_IMAGE_THRESHOLD:

            if usable_text and char_count >= self.MIN_TEXT_CHARS:
                page_type = "hybrid"
            else:
                page_type = "scanned"

        elif usable_text:

            page_type = "digital"

        elif (
            image_coverage > 0
            or char_count > 0
            or page.get_drawings()
        ):

            page_type = "ocr_required"

        else:

            page_type = "blank"

        return {
            "page_type": page_type,
            "character_count": char_count,
            "image_coverage": round(image_coverage, 4),
            "invalid_char_ratio": round(invalid_ratio, 4),
            "requires_ocr": page_type in {
                "scanned",
                "hybrid",
                "ocr_required",
            },
        }

    def _image_coverage(
        self,
        page: pymupdf.Page,
    ) -> float:

        page_rect = page.rect * page.derotation_matrix
        page_area = page_rect.get_area()

        if page_area <= 0:
            return 0.0

        image_area = 0.0

        for image in page.get_image_info():

            rect = pymupdf.Rect(image["bbox"])

            visible_rect = rect & page_rect

            image_area += visible_rect.get_area()

        return min(image_area / page_area, 1.0)