import re


SECTION_PREFIX = re.compile(
    r"^\s*\d{1,4}[A-Z]?\.\s*",
    re.IGNORECASE
)

SUBSECTION_PATTERN = re.compile(
    r"^\s*\((\d{1,3})\)\s*(.*)$"
)


def parse_subsections(section: dict) -> list[dict]:

    subsections = []
    current = None
    expected_subsection = 1

    def flush():

        if current is None:
            return

        if not current["lines"]:
            return

        subsections.append({
            "subsection_number": current["subsection_number"],
            "page_start": current["page_start"],
            "page_end": current["page_end"],
            "text": "\n".join(current["lines"]),
            "pages": current["pages"]
        })

    first_line = True

    for page_number, page_text in sorted(
        section["pages"].items(),
        key=lambda item: int(item[0])
    ):

        for raw_line in page_text.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            # Remove the section number from the opening line.
            if first_line:

                line = SECTION_PREFIX.sub(
                    "",
                    line,
                    count=1
                ).strip()

                first_line = False

                if not line:
                    continue

            match = SUBSECTION_PATTERN.match(line)

            # Detect sequential subsection boundaries.
            if (
                match
                and int(match.group(1))
                == expected_subsection
            ):

                flush()

                current = {
                    "subsection_number": match.group(1),
                    "page_start": page_number,
                    "page_end": page_number,
                    "lines": [],
                    "pages": {}
                }

                expected_subsection += 1

            # Handle sections without numbered subsections.
            if current is None:

                current = {
                    "subsection_number": None,
                    "page_start": page_number,
                    "page_end": page_number,
                    "lines": [],
                    "pages": {}
                }

            current["lines"].append(line)

            current["pages"].setdefault(
                page_number, []
            ).append(line)

            current["page_end"] = page_number

    flush()

    for subsection in subsections:

        subsection["pages"] = {
            page: "\n".join(lines)
            for page, lines in subsection["pages"].items()
        }

    return subsections