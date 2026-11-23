import pymupdf

from rag.ingestion.parsers.statute_index import (
    extract_section_titles
)


def main():

    pages = []

    with pymupdf.open("rag/test/BNSS2023.pdf") as pdf:

        for index in range(1, 19):

            pages.append({
                "page_number": index + 1,
                "text": pdf[index].get_text(
                    "text",
                    sort=True
                )
            })

    titles = extract_section_titles(
        pages=pages,
        start_page=2,
        end_page=19
    )

    print("\n========== STATUTE INDEX ==========")

    print("Total titles:", len(titles))

    for number in ["1", "14", "35", "36", "55", "531"]:

        print(
            f"Section {number}:",
            titles.get(number)
        )

    assert len(titles) == 531

    assert titles["35"] == (
        "When police may arrest without warrant"
    )

    assert titles["531"] == "Repeal and savings"

    print("\nAll tests passed.")


if __name__ == "__main__":
    main()