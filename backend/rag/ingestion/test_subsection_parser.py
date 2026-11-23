from rag.ingestion.parsers.subsection_parser import parse_subsections


section = {
    "section_number": "187",
    "pages": {
        125: """
187. (1) Whenever any person is arrested
and the investigation cannot be completed.
(2) The Magistrate may authorise detention
""",
        126: """
for a term not exceeding fifteen days.
(3) The Magistrate may authorise further detention.
(i) ninety days for serious offences;
(ii) sixty days for other offences.
(4) No Magistrate shall authorise police custody
unless the accused is produced in person.
"""
    }
}


subsections = parse_subsections(section)

print("\n========== SUBSECTION PARSING ==========")

for subsection in subsections:

    print(
        f"\nSubsection: {subsection['subsection_number']}"
    )

    print(
        f"Pages: {subsection['page_start']}"
        f"-{subsection['page_end']}"
    )

    print(subsection["text"])


assert len(subsections) == 4

assert subsections[1]["subsection_number"] == "2"

assert subsections[1]["page_start"] == 125

assert subsections[1]["page_end"] == 126

assert "fifteen days" in subsections[1]["text"]

assert "ninety days" in subsections[2]["text"]

assert "sixty days" in subsections[2]["text"]

print("\nAll tests passed.")