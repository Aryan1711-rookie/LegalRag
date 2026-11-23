import pymupdf

from rag.ingestion.parsers.statute_parser import (
    parse_statute_pages
)


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
            "36": "Procedure of arrest and duties of officer making arrest"
        }
    )

    print("\n========== STATUTE PARSING ==========")

    print("Total sections:", len(sections))

    section = next(
        s for s in sections
        if s["section_number"] == "35"
    )

    print("Section:", section["section_number"])
    print("Title:", section["section_title"])
    print("Chapter:", section["chapter"])
    print("Start page:", section["page_start"])
    print("End page:", section["page_end"])

    print("\n========== SECTION CONTENT ==========")

    for page_number, text in section["pages"].items():

        print(f"\n--- Page {page_number} ---")
        print(text)

    assert len(sections) == 531
    assert section["page_start"] == 61
    assert section["page_end"] == 63

    print("\nAll tests passed.")


if __name__ == "__main__":
    main()