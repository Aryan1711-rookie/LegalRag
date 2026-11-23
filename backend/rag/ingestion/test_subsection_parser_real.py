import re
import pymupdf

from rag.ingestion.parsers.statute_parser import (
    parse_statute_pages
)

from rag.ingestion.parsers.subsection_parser import (
    parse_subsections
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main():

    pdf_path = "rag/test/BNSS2023.pdf"

    pages = []

    with pymupdf.open(pdf_path) as pdf:

        for index in range(45, 262):

            page = pdf[index]

            pages.append({
                "page_number": index + 1,
                "text": page.get_text(
                    "text",
                    sort=True
                )
            })

    sections = parse_statute_pages(
        pages=pages,
        start_page=46,
        end_page=262,
        section_titles={
            "35": "When police may arrest without warrant",
            "36": "Procedure of arrest and duties of officer making arrest",
            "173": "Information in cognizable cases",
            "174": "Information as to non-cognizable cases and investigation of such cases",
            "187": "Procedure when investigation cannot be completed in twenty-four hours",
            "188": "Report of investigation by subordinate police officer"
        }
    )

    assert len(sections) == 531

    expected_counts = {
        "35": 7,
        "173": 4,
        "187": 10
    }

    for section_number, expected in expected_counts.items():

        section = next(
            s for s in sections
            if s["section_number"] == section_number
        )

        subsections = parse_subsections(section)

        print("\n" + "=" * 70)

        print("Section:", section_number)
        print("Title:", section["section_title"])
        print("Expected subsections:", expected)
        print("Parsed subsections:", len(subsections))

        print("=" * 70)

        for subsection in subsections:

            text = subsection["text"]

            print(
                f"\nSubsection: "
                f"{subsection['subsection_number']}"
            )

            print(
                f"Pages: {subsection['page_start']}"
                f"-{subsection['page_end']}"
            )

            print("Characters:", len(text))
            print("Estimated tokens:", len(text) // 4)

            print("\nContent:")
            print(text)

        # Verify subsection count.
        assert len(subsections) == expected, (
            f"Section {section_number}: "
            f"expected {expected} subsections, "
            f"got {len(subsections)}"
        )

        # Verify subsection numbering.
        actual_numbers = [
            s["subsection_number"]
            for s in subsections
        ]

        expected_numbers = [
            str(i)
            for i in range(1, expected + 1)
        ]

        assert actual_numbers == expected_numbers

        # Verify that no statutory content was lost.
        original_text = "\n".join(
            section["pages"].values()
        )

        original_text = re.sub(
            r"^\s*\d{1,4}[A-Z]?\.\s*",
            "",
            original_text,
            count=1
        )

        reconstructed_text = "\n".join(
            s["text"] for s in subsections
        )

        assert normalize(original_text) == normalize(
            reconstructed_text
        ), f"Content mismatch in Section {section_number}"

        print("\nPASS: Subsection count")
        print("PASS: Sequential numbering")
        print("PASS: Content preservation")

    print("\nAll real subsection parsing tests passed.")


if __name__ == "__main__":
    main()