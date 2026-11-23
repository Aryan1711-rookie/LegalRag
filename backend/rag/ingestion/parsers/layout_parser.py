import re

import pymupdf


def is_page_number(text, bbox, page_rect):
    if not re.fullmatch(r"\d{1,4}", text):
        return False

    x0, y0, x1, y1 = bbox

    center_x = (x0 + x1) / 2

    relative_x = (
        center_x - page_rect.x0
    ) / page_rect.width

    relative_y = (
        y0 - page_rect.y0
    ) / page_rect.height

    is_centered = 0.40 <= relative_x <= 0.60

    is_header = relative_y < 0.12
    is_footer = relative_y > 0.90

    return is_centered and (
        is_header or is_footer
    )


def extract_layout_text(
    page: pymupdf.Page,
    remove_page_numbers: bool = False
):

    blocks = page.get_text(
        "dict",
        sort=True
    )["blocks"]

    extracted_blocks = []

    for block in blocks:

        if block.get("type") != 0:
            continue

        lines = []

        for line in block.get("lines", []):

            text = "".join(
                span["text"]
                for span in line["spans"]
            ).strip()

            if not text:
                continue

            if remove_page_numbers and is_page_number(
                text,
                line["bbox"],
                page.rect
            ):
                continue

            lines.append(text)

        if lines:
            extracted_blocks.append(
                "\n".join(lines)
            )

    return "\n\n".join(extracted_blocks)