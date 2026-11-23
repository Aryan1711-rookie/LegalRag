import re


PAGE_HEADER = re.compile(
    r"^\s*p\s*a\s*g\s*e\s*\|\s*\d+\s*$",
    re.IGNORECASE
)

SECTION_PATTERN = re.compile(
    r"^\s*(\d{1,4}[A-Z]?)\.\s+(.+)$"
)

CHAPTER_PATTERN = re.compile(
    r"^\s*CHAPTER\s+([IVXLCDM]+)\s*$",
    re.IGNORECASE
)


def remove_page_headers(text: str) -> str:

    return "\n".join(
        line
        for line in text.splitlines()
        if not PAGE_HEADER.fullmatch(line)
    )


def detect_section(line: str):

    match = SECTION_PATTERN.match(line)

    if not match:
        return None

    return {
        "section_number": match.group(1),
        "text": match.group(2).strip()
    }


def detect_chapter(line: str):

    match = CHAPTER_PATTERN.match(line)

    if not match:
        return None

    return match.group(1).upper()


def parse_statute_pages(
    pages: list,
    start_page: int,
    end_page: int,
    first_section: int = 1,
    section_titles: dict | None = None
):

    section_titles = section_titles or {}

    sections = []

    current_section = None
    current_chapter = None

    expected_section = first_section

    def flush():

        if current_section is not None:
            sections.append(current_section)

    for page in pages:

        page_number = page["page_number"]

        if not start_page <= page_number <= end_page:
            continue

        text = (
            page.get("layout_text")
            or page.get("text", "")
        )

        text = remove_page_headers(text)

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line in lines:

            # 1. Detect chapter boundaries

            chapter = detect_chapter(line)

            if chapter:

                flush()

                current_section = None
                current_chapter = chapter

                continue

            # 2. Detect section boundaries

            section = detect_section(line)

            if (
                section
                and section["section_number"]
                == str(expected_section)
            ):

                section_number = section[
                    "section_number"
                ]

                next_title = section_titles.get(
                    section_number
                )

                # 3. Remove the next section's heading
                # from the previous section's content.

                if current_section and next_title:

                    previous_page = current_section[
                        "page_end"
                    ]

                    previous_lines = current_section[
                        "pages"
                    ].get(previous_page, [])

                    if previous_lines:

                        last_line = (
                            previous_lines[-1]
                            .strip()
                            .rstrip(".")
                        )

                        expected_title = (
                            next_title
                            .strip()
                            .rstrip(".")
                        )

                        if (
                            last_line.casefold()
                            == expected_title.casefold()
                        ):

                            previous_lines.pop()

                            if not previous_lines:
                                del current_section[
                                    "pages"
                                ][previous_page]

                                if current_section["pages"]:
                                    current_section["page_end"] = max(
                                        current_section["pages"]
                                    )

                # 4. Save the previous section

                flush()

                # 5. Initialize the next section

                current_section = {
                    "section_number": section_number,
                    "section_title": next_title,
                    "chapter": current_chapter,
                    "page_start": page_number,
                    "page_end": page_number,
                    "pages": {}
                }

                expected_section += 1

            # 6. Preserve content across pages

            if current_section is not None:

                current_section["page_end"] = page_number

                current_section["pages"].setdefault(
                    page_number, []
                ).append(line)

    # 7. Save the final section

    flush()

    # 8. Convert line lists into page text

    for section in sections:

        section["pages"] = {
            page_number: "\n".join(lines)
            for page_number, lines in section["pages"].items()
        }

    return sections