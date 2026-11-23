import re

class SectionExpander:

    MAX_SECTION_CHUNKS = 100
    MAX_CONTEXT_CHARACTERS = 32000

    MAX_SUPPORT_CHUNKS = 3
    SUPPORT_WEIGHT = 0.25

    def __init__(self, search_repository):

        self.search_repository = search_repository

    @staticmethod
    def tokenize(text: str) -> set:

        return set(
            re.findall(
                r"\b\w{3,}\b",
                text.lower()
            )
        )

    def expand(
        self,
        question: str,
        retrieved_chunks: list,
        document_id: str | None = None
    ):

        if not document_id:
            return retrieved_chunks

        requested_provisions = (
            self.extract_provision_references(question)
        )

        # Exact statutory provision retrieval
        if requested_provisions:

            exact_chunks = []
            missing_provisions = []

            section_cache = {}

            for provision in requested_provisions:

                section_number = provision["section_number"]

                subsection_number = provision[
                    "subsection_number"
                ]

                # Avoid repeated database calls for the same section.
                if section_number not in section_cache:

                    section_cache[section_number] = (
                        self.search_repository.get_section_chunks(
                            document_id=document_id,
                            section_number=section_number,
                            limit=self.MAX_SECTION_CHUNKS + 1
                        )
                    )

                section_chunks = section_cache[section_number]

                if len(section_chunks) > self.MAX_SECTION_CHUNKS:

                    print(
                        f"Section {section_number} "
                        "exceeds chunk limit."
                    )

                    return []

                # Filter by subsection when explicitly requested.
                if subsection_number is not None:

                    matched_chunks = [
                        chunk
                        for chunk in section_chunks
                        if str(
                            (chunk.get("metadata") or {}).get(
                                "subsection_number"
                            )
                        ) == subsection_number
                    ]

                else:

                    matched_chunks = section_chunks

                if not matched_chunks:

                    missing_provisions.append(provision)

                    continue

                exact_chunks.extend(matched_chunks)

            # Prevent incomplete multi-provision responses.
            if missing_provisions:

                print("Missing provisions:", missing_provisions)

                return []

            # Deduplicate chunks while preserving order.
            unique_chunks = {
                chunk["id"]: chunk
                for chunk in exact_chunks
            }

            expanded = list(unique_chunks.values())

            total_characters = sum(
                len(chunk.get("content") or "")
                for chunk in expanded
            )

            if total_characters > self.MAX_CONTEXT_CHARACTERS:

                print("Exact provision exceeds context budget.")

                return []

            print("\n========== EXACT PROVISION RETRIEVAL ==========")

            print("Requested provisions:", requested_provisions)
            print("Retrieved chunks:", len(expanded))
            print("Context characters:", total_characters)

            print("===============================================\n")

            return expanded
        # Semantic or hybrid section expansion
        if not retrieved_chunks:
            return retrieved_chunks

        ranked_sections = self.rank_section_candidates(
            question=question,
            retrieved_chunks=retrieved_chunks,
            document_id=document_id
        )

        if not ranked_sections:
            return retrieved_chunks

        # Select strongest section
        best_section = ranked_sections[0]

        section_number = best_section["section_number"]

        print("\n========== SECTION CANDIDATES ==========")

        for candidate in ranked_sections:

            print(
                f"Section {candidate['section_number']} | "
                f"{candidate['section_title']} | "
                f"Chunks: {candidate['matched_chunks']} | "
                f"Strategy: {candidate['strategy']} | "
                f"Score: {candidate['score']:.6f}"
            )

        print("========================================\n")

        # Retrieve complete section
        section_chunks = (
            self.search_repository.get_section_chunks(
                document_id=document_id,
                section_number=section_number,
                limit=self.MAX_SECTION_CHUNKS + 1
            )
        )

        if not section_chunks:
            return retrieved_chunks

        if len(section_chunks) > self.MAX_SECTION_CHUNKS:
            print(f"Section {section_number} exceeds chunk limit.")
            return retrieved_chunks

        # Deduplicate chunks
        expanded_chunks = list(section_chunks)

        existing_ids = {
            chunk["id"]
            for chunk in expanded_chunks
        }

        for chunk in retrieved_chunks:

            if chunk["id"] not in existing_ids:

                expanded_chunks.append(chunk)
                existing_ids.add(chunk["id"])

        # Protect the context budget
        total_characters = sum(
            len(chunk.get("content") or "")
            for chunk in expanded_chunks
        )

        if total_characters > self.MAX_CONTEXT_CHARACTERS:
            return retrieved_chunks

        print("\n========== SECTION EXPANSION ==========")
        print("Section:", section_number)
        print("Title:", best_section["section_title"])
        print("Original chunks:", len(retrieved_chunks))
        print("Section chunks:", len(section_chunks))
        print("Expanded chunks:", len(expanded_chunks))
        print("Context characters:", total_characters)
        print("=======================================\n")

        return expanded_chunks

    @staticmethod
    def extract_section_numbers(
        question: str
    ) -> list[str]:

        references = (
            SectionExpander.extract_provision_references(
                question
            )
        )

        return list(dict.fromkeys(
            reference["section_number"]
            for reference in references
        ))
    def rank_section_candidates(
        self,
        question: str,
        retrieved_chunks: list,
        document_id: str
    ) -> list[dict]:

        question_tokens = self.tokenize(question)

        is_hybrid = any(
            chunk.get("rrf_score") is not None
            for chunk in retrieved_chunks
        )

        candidates = {}
        seen_ids = set()

        for chunk in retrieved_chunks:

            metadata = chunk.get("metadata") or {}

            document_type = metadata.get("document_type")
            section_number = metadata.get("section_number")
            section_title = metadata.get("section_title") or ""

            if chunk.get("document_id") != document_id:
                continue

            if document_type not in {"act", "bill"}:
                continue

            if not section_number:
                continue

            chunk_id = chunk.get("id") or chunk.get("chunk_id")

            if chunk_id in seen_ids:
                continue

            seen_ids.add(chunk_id)

            section_number = str(section_number)

            title_tokens = self.tokenize(section_title)

            title_coverage = (
                len(question_tokens & title_tokens)
                / len(title_tokens)
                if title_tokens else 0.0
            )

            # Hybrid retrieval scoring
            if is_hybrid:

                score = float(
                    chunk.get("rrf_score") or 0
                )

            # Existing dense retrieval scoring
            else:

                similarity = float(
                    chunk.get("similarity") or 0
                )

                score = (
                    0.65 * title_coverage
                    + 0.35 * similarity
                )

            if section_number not in candidates:

                candidates[section_number] = {
                    "section_number": section_number,
                    "section_title": section_title,
                    "scores": [],
                    "matched_chunks": 0
                }

            candidates[section_number]["scores"].append(score)

            candidates[section_number]["matched_chunks"] += 1

        ranked_sections = []

        for candidate in candidates.values():

            scores = sorted(
                candidate.pop("scores"),
                reverse=True
            )

            strongest_score = scores[0]

            if is_hybrid:

                supporting_score = sum(
                    scores[1:self.MAX_SUPPORT_CHUNKS]
                )

                final_score = (
                    strongest_score
                    + self.SUPPORT_WEIGHT * supporting_score
                )

            else:

                final_score = strongest_score

            candidate["score"] = final_score

            candidate["strategy"] = (
                "hybrid" if is_hybrid else "dense"
            )

            ranked_sections.append(candidate)

        return sorted(
            ranked_sections,
            key=lambda candidate: candidate["score"],
            reverse=True
        )

    @staticmethod
    def extract_provision_references(
        question: str
    ) -> list[dict]:

        provision = (
            r"\d{1,4}[A-Z]?"
            r"(?:\s*\(\d{1,3}[A-Z]?\))?"
        )

        # Separator between listed provisions. Accepts "," , "and",
        # "or", "&", "और", and the Oxford-comma form ", and" / ", or".
        separator = (
            r"\s*(?:,\s*(?:and|or|&|और)?|(?:and|or|&|और))\s*"
        )

        pattern = (
            r"\b(?:sections?|secs?\.?|clauses?|धारा)\s+"
            rf"({provision}"
            rf"(?:{separator}{provision})*)"
        )

        matches = re.findall(
            pattern,
            question,
            flags=re.IGNORECASE
        )

        references = []
        seen = set()

        for match in matches:

            provisions = re.findall(
                r"(\d{1,4}[A-Z]?)"
                r"(?:\s*\((\d{1,3}[A-Z]?)\))?",
                match,
                flags=re.IGNORECASE
            )

            for section, subsection in provisions:

                section = section.upper()

                subsection = (
                    subsection.upper()
                    if subsection
                    else None
                )

                key = (section, subsection)

                if key in seen:
                    continue

                seen.add(key)

                references.append({
                    "section_number": section,
                    "subsection_number": subsection
                })

        return references