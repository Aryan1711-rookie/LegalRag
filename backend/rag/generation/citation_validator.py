import re


class CitationValidator:

    CITATION_PATTERN = re.compile(
        r"\[\s*(Source\b[^\]\r\n]*)\]"
        r"|【\s*(Source\b[^】\r\n]*)】"
        r"|\*\*\s*(Source\b[^*\r\n]*)\*\*",
        re.IGNORECASE
    )

    BODY_PATTERN = re.compile(
        r"Source\s+(\d+)"
        r"(?:\s*[,·]\s*Pages?\s+(\d+)"
        r"(?:\s*[-–—]\s*(\d+))?)?",
        re.IGNORECASE
    )

    @staticmethod
    def get_page_range(source: dict):

        page_start = source.get("page_start")
        page_end = source.get("page_end")

        if page_start is None:
            page_start = source.get("page")

        if page_end is None:
            page_end = page_start

        try:
            page_start = int(str(page_start))
            page_end = int(str(page_end))

        except (ValueError, TypeError):
            return None, None

        if page_start < 1 or page_end < page_start:
            return None, None

        return page_start, page_end

    @staticmethod
    def format_citation(
        source_number: int,
        page_start: int,
        page_end: int
    ) -> str:

        if page_start == page_end:
            return (
                f"[Source {source_number}, "
                f"Page {page_start}]"
            )

        return (
            f"[Source {source_number}, "
            f"Pages {page_start}-{page_end}]"
        )

    def normalize(
        self,
        answer: str,
        sources: list[dict]
    ) -> str:

        source_lookup = {
            source["source"]: source
            for source in sources
        }

        def replace_citation(match):

            body = next(
                group for group in match.groups()
                if group is not None
            ).strip()

            parsed = self.BODY_PATTERN.fullmatch(body)

            if not parsed:
                return match.group(0)

            source_number = int(parsed.group(1))

            source = source_lookup.get(source_number)

            if source is None:
                return match.group(0)

            # Resolve missing pages using trusted metadata.
            if parsed.group(2) is None:

                page_start, page_end = (
                    self.get_page_range(source)
                )

                if page_start is None:
                    return match.group(0)

            else:

                # Preserve explicitly supplied pages.
                page_start = int(parsed.group(2))

                page_end = (
                    int(parsed.group(3))
                    if parsed.group(3) is not None
                    else page_start
                )

            return self.format_citation(
                source_number,
                page_start,
                page_end
            )

        return self.CITATION_PATTERN.sub(
            replace_citation,
            answer
        )

    def validate(
        self,
        answer: str,
        sources: list[dict]
    ) -> dict:

        source_lookup = {
            source["source"]: source
            for source in sources
        }

        matches = list(
            self.CITATION_PATTERN.finditer(answer)
        )

        valid_citations = []
        invalid_citations = []

        for match in matches:

            body = next(
                group for group in match.groups()
                if group is not None
            ).strip()

            parsed = self.BODY_PATTERN.fullmatch(body)

            # Check 1: Citation format.
            if not parsed:

                invalid_citations.append({
                    "citation": match.group(0),
                    "reason": "Malformed citation"
                })

                continue

            source_number = int(parsed.group(1))

            source = source_lookup.get(source_number)

            # Check 2: Source exists.
            if source is None:

                invalid_citations.append({
                    "source": source_number,
                    "citation": match.group(0),
                    "reason": "Source does not exist in retrieved context"
                })

                continue

            # Check 3: Page number exists.
            if parsed.group(2) is None:

                invalid_citations.append({
                    "source": source_number,
                    "page": None,
                    "reason": "Missing page number"
                })

                continue

            page_start = int(parsed.group(2))

            page_end = (
                int(parsed.group(3))
                if parsed.group(3) is not None
                else page_start
            )

            # Check 4: Valid page range.
            if page_start < 1 or page_end < page_start:

                invalid_citations.append({
                    "source": source_number,
                    "citation": match.group(0),
                    "reason": "Invalid page range"
                })

                continue

            expected_start, expected_end = (
                self.get_page_range(source)
            )

            # Check 5: Trusted source metadata exists.
            if expected_start is None:

                invalid_citations.append({
                    "source": source_number,
                    "citation": match.group(0),
                    "reason": "Source has invalid page metadata"
                })

                continue

            # Check 6: Citation must match the registered range.
            if (
                page_start != expected_start
                or page_end != expected_end
            ):

                invalid_citations.append({
                    "source": source_number,
                    "page_start": page_start,
                    "page_end": page_end,
                    "expected_page_start": expected_start,
                    "expected_page_end": expected_end,
                    "reason": "Page range does not match source registry"
                })

                continue

            page_display = (
                str(page_start)
                if page_start == page_end
                else f"{page_start}-{page_end}"
            )

            valid_citations.append({
                "source": source_number,
                "document": source["document"],
                "page": source.get("page", page_start),
                "page_start": page_start,
                "page_end": page_end,
                "page_display": page_display,
                "chunk_id": source["chunk_id"],
                "section_number": source.get("section_number"),
                "subsection_number": source.get("subsection_number"),
                "provision_reference": source.get("provision_reference")
            })

        unique_citations = {
            (
                citation["source"],
                citation["page_start"],
                citation["page_end"]
            )
            for citation in valid_citations
        }

        return {
            "total_citations": len(matches),

            "valid_citations": valid_citations,

            "invalid_citations": invalid_citations,

            "all_valid": (
                len(matches) > 0
                and not invalid_citations
            ),

            "unique_valid_citations": len(
                unique_citations
            )
        }