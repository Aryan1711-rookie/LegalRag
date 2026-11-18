
import re


class CitationValidator:

    CITATION_PATTERN = re.compile(
        r"\[Source\s*(\d+),\s*Page\s*(\d+)\]",
        re.IGNORECASE
    )

    def validate(self, answer: str, sources: list[dict]) -> dict:

        source_lookup = {
            source["source"]: source
            for source in sources
        }

        matches = self.CITATION_PATTERN.findall(answer)

        valid_citations = []
        invalid_citations = []

        for source_number, page_number in matches:

            source_number = int(source_number)
            page_number = int(page_number)

            source = source_lookup.get(source_number)

            if source is None:
                invalid_citations.append({
                    "source": source_number,
                    "page": page_number,
                    "reason": "Source does not exist in retrieved context"
                })
                continue

            if str(source["page"]) != str(page_number):
                invalid_citations.append({
                    "source": source_number,
                    "page": page_number,
                    "reason": "Page number does not match source registry"
                })
                continue

            valid_citations.append({
                "source": source_number,
                "document": source["document"],
                "page": source["page"],
                "chunk_id": source["chunk_id"]
            })

        # Calculate unique citations
        unique_citations = {
            (
                citation["source"],
                citation["page"]
            )
            for citation in valid_citations
        }

        return {
            "total_citations": len(matches),
            "valid_citations": valid_citations,
            "invalid_citations": invalid_citations,
            "all_valid": (
                len(matches) > 0
                and len(invalid_citations) == 0
            ),
            "unique_valid_citations": len(unique_citations)
        }
