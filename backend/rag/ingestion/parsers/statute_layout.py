import re


def detect_statute_layout(pages: list):

    index_start = None
    index_end = None

    body_start = None
    body_end = None

    for page in pages:

        page_number = page["page_number"]

        text = page.get("text", "")

        text = re.sub(
            r"\s+", " ", text
        ).strip().lower()

        # Detect index
        if index_start is None and (
            "arrangement of sections" in text
            or "arrangement of clauses" in text
        ):
            index_start = page_number

        # Detect comparison table
        if (
            index_start is not None
            and index_end is None
            and "corresponding section table" in text
            and page_number > index_start
        ):
            index_end = page_number - 1

        # Detect actual statutory body
        if (
            body_start is None
            and index_start is not None
            and page_number > index_start
            and re.search(
                r"\b1\.\s*\(1\)\s*this\s+(?:act|sanhita)",
                text
            )
        ):
            body_start = page_number

            if index_end is None:
                index_end = page_number - 1

        # Detect schedules after statutory body
        if (
            body_start is not None
            and page_number > body_start
        ):

            lines = page.get("text", "").splitlines()

            if any(
                re.fullmatch(
                    r"(?:THE\s+)?FIRST\s+SCHEDULE",
                    line.strip(),
                    re.IGNORECASE
                )
                for line in lines
            ):
                body_end = page_number - 1
                break

    if body_start is not None and body_end is None:
        body_end = pages[-1]["page_number"]

    if None in (
        index_start,
        index_end,
        body_start,
        body_end
    ):
        return None

    if not (
        index_start <= index_end
        < body_start <= body_end
    ):
        return None

    return {
        "index_start": index_start,
        "index_end": index_end,
        "body_start": body_start,
        "body_end": body_end
    }