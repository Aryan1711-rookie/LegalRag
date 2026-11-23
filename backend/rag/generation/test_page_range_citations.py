from rag.generation.citation_validator import CitationValidator


def main():

    validator = CitationValidator()

    sources = [
        {
            "source": 1,
            "document": "BNSS2023.pdf",
            "page": 125,
            "page_start": 125,
            "page_end": 126,
            "chunk_id": "chunk_001",
            "section_number": "187",
            "subsection_number": "2",
            "provision_reference": "187(2)"
        },
        {
            "source": 2,
            "document": "BNSS2023.pdf",
            "page": 126,
            "page_start": 126,
            "page_end": 126,
            "chunk_id": "chunk_002"
        },
        {
            "source": 3,
            "document": "Judgment.pdf",
            "page": 15,
            "chunk_id": "chunk_003"
        }
    ]

    test_cases = [
        ("[Source 1]", True),
        ("【Source 1】", True),
        ("[Source 1, Pages 125-126]", True),
        ("[Source 1, Pages 125–126]", True),
        ("**Source 1 · Pages 125-126**", True),

        ("[Source 1, Page 125]", False),
        ("[Source 1, Pages 125-127]", False),
        ("[Source 1, Pages 126-125]", False),

        ("[Source 2, Page 126]", True),
        ("[Source 2]", True),

        ("[Source 3, Page 15]", True),
        ("[Source 3]", True),

        ("[Source 99]", False),
        ("[Source 1, Page abc]", False),
        ("Answer without citations.", False)
    ]

    passed = 0

    for answer, expected in test_cases:

        normalized = validator.normalize(
            answer,
            sources
        )

        report = validator.validate(
            normalized,
            sources
        )

        actual = report["all_valid"]

        success = actual == expected

        if success:
            passed += 1

        print(
            f"{'PASS' if success else 'FAIL'} | "
            f"{answer} -> {normalized} | "
            f"Valid: {actual}"
        )

    print("\n========== SUMMARY ==========")
    print("Passed:", passed)
    print("Total:", len(test_cases))

    assert passed == len(test_cases)

    print("\nAll page-range citation tests passed.")


if __name__ == "__main__":
    main()