import re

from rag.ingestion.parsers.statute_parser import (
    remove_page_headers
)


INDEX_ENTRY = re.compile(
    r"^\s*(\d{1,4}[A-Z]?)\.\s+(.+)$"
)

STOP_PATTERN = re.compile(
    r"^(CHAPTER\b|THE (FIRST|SECOND) SCHEDULE|Note:)",
    re.IGNORECASE
)


def extract_section_titles(
    pages: list,
    start_page: int,
    end_page: int
) -> dict:

    titles = {}

    current_section = None
    expected_section = 1

    for page in pages:

        page_number = page["page_number"]

        if not start_page <= page_number <= end_page:
            continue

        text = (
            page.get("layout_text")
            or page.get("text", "")
        )

        text = remove_page_headers(text)

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            if STOP_PATTERN.match(line):

                current_section = None
                continue

            match = INDEX_ENTRY.match(line)

            if (
                match
                and match.group(1) == str(expected_section)
            ):

                current_section = match.group(1)

                titles[current_section] = (
                    match.group(2).strip()
                )

                expected_section += 1

                continue

            # Handle titles spanning multiple lines

            if (
                current_section
                and not titles[current_section].endswith(".")
            ):

                titles[current_section] += " " + line

    return {
        number: re.sub(r"\s+", " ", title).strip().rstrip(".")
        for number, title in titles.items()
    }