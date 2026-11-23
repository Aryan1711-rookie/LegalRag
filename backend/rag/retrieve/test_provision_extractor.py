from rag.retrieve.section_expander import SectionExpander


def main():

    test_cases = [
        (
            "Explain Section 187",
            [("187", None)]
        ),
        (
            "Explain Section 187(2)",
            [("187", "2")]
        ),
        (
            "Compare Sections 187(2) and 187(3)",
            [("187", "2"), ("187", "3")]
        ),
        (
            "Explain Sections 35 and 173",
            [("35", None), ("173", None)]
        ),
        (
            "Explain Sec. 35(1)",
            [("35", "1")]
        ),
        (
            "Compare Section 35(1) with Section 173(2)",
            [("35", "1"), ("173", "2")]
        ),
        (
            "Explain Section 187 (2)",
            [("187", "2")]
        ),
        (
            "Explain Clause 12(3)",
            [("12", "3")]
        ),
        (
            "धारा 35(1)",
            [("35", "1")]
        ),
        (
            "What is Zero FIR?",
            []
        )
    ]

    for question, expected in test_cases:

        references = (
            SectionExpander.extract_provision_references(
                question
            )
        )

        actual = [
            (
                reference["section_number"],
                reference["subsection_number"]
            )
            for reference in references
        ]

        assert actual == expected, (
            f"Question: {question}\n"
            f"Expected: {expected}\n"
            f"Actual: {actual}"
        )

        print(f"PASS | {question} -> {actual}")

    print("\nAll provision extraction tests passed.")


if __name__ == "__main__":
    main()