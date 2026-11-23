from rag.generation.citation_validator import CitationValidator


validator = CitationValidator()

sources = [
    {
        "source": 1,
        "document": "BNSS 2023",
        "page": 125,
        "chunk_id": "chunk_00729"
    },
    {
        "source": 2,
        "document": "BNSS 2023",
        "page": 126,
        "chunk_id": "chunk_00733"
    }
]

test_cases = [
    ("[Source 1, Page 125]", True),
    ("【Source 1】", True),
    ("[Source 2]", True),
    ("【Source 2, Page 126】", True),
    ("**Source 2 · Page 126**", True),
    ("【Source\u202f2】", True),

    ("[Source 1, Page 999]", False),
    ("[Source 99]", False),
    ("[Source 99, Page 126]", False),
    ("[Source 1, Page abc]", False),
    ("Answer without citations.", False)
]

for answer, expected in test_cases:

    normalized = validator.normalize(
        answer,
        sources
    )

    report = validator.validate(
        normalized,
        sources
    )

    assert report["all_valid"] == expected, report

    print(
        f"PASS | {answer} -> {normalized} | "
        f"Valid: {report['all_valid']}"
    )

print("\nAll citation validation tests passed.")