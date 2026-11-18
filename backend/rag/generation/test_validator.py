from rag.generation.citation_validator import CitationValidator

sources = [
    {
        "source": 1,
        "document": "LANDMARK JUDGMENTS OF THE SUPREME COURT.pdf",
        "page": 13,
        "chunk_id": "chunk_00026"
    },
    {
        "source": 2,
        "document": "LANDMARK JUDGMENTS OF THE SUPREME COURT.pdf",
        "page": 15,
        "chunk_id": "chunk_00032"
    }
]

answer = """
The Indira Gandhi case is discussed in the document.
[Source 1, Page 13]

The Kesavananda Bharati case is discussed here.
[Source 2, Page 99]

This citation does not exist.
[Source 5, Page 20]
"""

validator = CitationValidator()
result = validator.validate(answer, sources)

print("\n========== CITATION VALIDATION ==========\n")
print(result)