from unittest.mock import Mock

from rag.retrieve.section_expander import SectionExpander


def make_chunk(
    chunk_id,
    section,
    subsection,
    part=1
):

    return {
        "id": chunk_id,
        "chunk_id": chunk_id,
        "document_id": "test-document",
        "content": f"Section {section}({subsection}), Part {part}",
        "metadata": {
            "document_type": "act",
            "section_number": section,
            "subsection_number": subsection,
            "subsection_part": part
        }
    }


def main():

    repository = Mock()

    section_data = {
        "187": [
            make_chunk("chunk_1", "187", "1"),
            make_chunk("chunk_2", "187", "2"),
            make_chunk("chunk_3", "187", "3"),
            make_chunk("chunk_4", "187", "4")
        ],
        "35": [
            make_chunk("chunk_5", "35", "1", 1),
            make_chunk("chunk_6", "35", "1", 2),
            make_chunk("chunk_7", "35", "2")
        ]
    }

    def get_section_chunks(
        document_id,
        section_number,
        limit
    ):
        return section_data.get(section_number, [])[:limit]

    repository.get_section_chunks.side_effect = (
        get_section_chunks
    )

    expander = SectionExpander(repository)

    test_cases = [
        (
            "Complete section",
            "Explain Section 187",
            ["chunk_1", "chunk_2", "chunk_3", "chunk_4"],
            1
        ),
        (
            "Exact subsection",
            "Explain Section 187(2)",
            ["chunk_2"],
            1
        ),
        (
            "Multiple subsections",
            "Compare Sections 187(2) and 187(3)",
            ["chunk_2", "chunk_3"],
            1
        ),
        (
            "Split subsection",
            "Explain Section 35(1)",
            ["chunk_5", "chunk_6"],
            1
        ),
        (
            "Multiple sections",
            "Compare Sections 35 and 187",
            [
                "chunk_5", "chunk_6", "chunk_7",
                "chunk_1", "chunk_2", "chunk_3", "chunk_4"
            ],
            2
        ),
        (
            "Missing subsection",
            "Explain Section 187(99)",
            [],
            1
        ),
        (
            "Missing section",
            "Explain Section 999",
            [],
            1
        ),
        (
            "Incomplete comparison",
            "Compare Sections 187(2) and 187(99)",
            [],
            1
        ),
        (
            "Deduplicate overlapping provisions",
            "Compare Sections 187 and 187(2)",
            ["chunk_1", "chunk_2", "chunk_3", "chunk_4"],
            1
        )
    ]

    passed = 0

    for name, question, expected, expected_calls in test_cases:

        repository.get_section_chunks.reset_mock()

        result = expander.expand(
            question=question,
            retrieved_chunks=[],
            document_id="test-document"
        )

        actual = [
            chunk["chunk_id"]
            for chunk in result
        ]

        assert actual == expected, (
            f"{name}: Expected {expected}, got {actual}"
        )

        assert (
            repository.get_section_chunks.call_count
            == expected_calls
        ), f"{name}: Unexpected database call count"

        passed += 1

        print(f"PASS | {name} | Chunks: {len(actual)}")

    print("\n========== SUMMARY ==========")
    print("Passed:", passed)
    print("Total:", len(test_cases))

    print("\nAll provision retrieval tests passed.")


if __name__ == "__main__":
    main()