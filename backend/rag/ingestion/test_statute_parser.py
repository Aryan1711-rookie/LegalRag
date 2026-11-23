from rag.ingestion.parsers.statute_parser import (
    remove_page_headers,
    detect_section,
    detect_chapter
)

from rag.ingestion.parsers.subsection_parser import (parse_subsections)
def main():

    text = """
P a g e | 61
CHAPTER V
ARREST OF PERSONS
When police may arrest without warrant.
35. (1) Any police officer may arrest
"""

    cleaned_text = remove_page_headers(text)

    for line in cleaned_text.splitlines():

        chapter = detect_chapter(line)

        if chapter:
            print("Chapter:", chapter)

        section = detect_section(line)

        if section:
            print("Section:", section)

    assert "P a g e | 61" not in cleaned_text

    assert detect_section(
        "35. (1) Any police officer"
    )["section_number"] == "35"

    assert detect_section("(3) The police officer") is None

    print("All tests passed.")

    target_sections = {"35", "173", "187"}

    for section in sections:

        if str(section["section_number"]) not in target_sections:
            continue

        subsections = parse_subsections(section)

        print("\n" + "=" * 70)

        print("Section:", section["section_number"])
        print("Title:", section["section_title"])
        print("Total subsections:", len(subsections))

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


if __name__ == "__main__":
    main()