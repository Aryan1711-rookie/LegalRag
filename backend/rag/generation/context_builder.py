class ContextBuilder:

    def __init__(self, retrieval_service):
        self.retrieval_service = retrieval_service

    def build_context_payload(
        self,
        query: str,
        document_id: str | None = None,
        user_id: str | None = None
    ) -> dict:

        retrieved_docs, retrieval_performance = (
            self.retrieval_service.retrieve_hybrid_with_metrics(
                question=query,
                document_id=document_id,
                user_id=user_id
            )
        )

        if not retrieved_docs:
            return {
                "context": "No relevant legal documents found.",
                "sources": [],
                "retrieval_performance": retrieval_performance
            }

        context_parts = []
        sources = []

        for index, doc in enumerate(
            retrieved_docs,
            start=1
        ):

            metadata = doc.get("metadata") or {}

            chunk_id = doc.get("chunk_id", "Unknown")
            content = doc.get("content", "")
            similarity = doc.get("similarity")

            source = metadata.get("source") or "Unknown source"

            # 1. Page metadata
            page_number = metadata.get("page_number", "Unknown")

            page_start = metadata.get("page_start")

            if page_start is None:
                page_start = page_number

            page_end = metadata.get("page_end")

            if page_end is None:
                page_end = page_start

            page_display = (
                str(page_start)
                if str(page_start) == str(page_end)
                else f"{page_start}-{page_end}"
            )

            page_label = (
                "Page"
                if str(page_start) == str(page_end)
                else "Pages"
            )

            # 2. Document metadata
            document_type = metadata.get("document_type")
            document_title = metadata.get("document_title")

            section_number = metadata.get("section_number")
            section_title = metadata.get("section_title")

            subsection_number = metadata.get(
                "subsection_number"
            )

            subsection_part = metadata.get(
                "subsection_part", 1
            )

            subsection_total_parts = metadata.get(
                "subsection_total_parts", 1
            )

            chapter = metadata.get("chapter")
            case_name = metadata.get("case_name")

            # 3. Build complete statutory reference
            provision_reference = None

            if section_number is not None:

                provision_reference = str(section_number)

                if subsection_number is not None:
                    provision_reference += (
                        f"({subsection_number})"
                    )

            # 4. Structured source registry
            sources.append({
                "source": index,
                "document": source,
                "document_title": document_title,
                "document_type": document_type,

                "page": page_number,
                "page_start": page_start,
                "page_end": page_end,
                "page_display": page_display,

                "chunk_id": chunk_id,
                "chapter": chapter,

                "section_number": section_number,
                "section_title": section_title,

                "subsection_number": subsection_number,
                "subsection_part": subsection_part,
                "subsection_total_parts": subsection_total_parts,

                "provision_reference": provision_reference,

                "case_name": case_name,
                "similarity": similarity,
                "content": content
            })

            # 5. Build LLM context
            context_lines = [
                f"[Source {index}]",
                f"Chunk ID: {chunk_id}",
                f"Document: {document_title or source}",
                f"{page_label}: {page_display}"
            ]

            if document_type:
                context_lines.append(
                    f"Document Type: {document_type}"
                )

            if chapter:
                context_lines.append(
                    f"Chapter: {chapter}"
                )

            if provision_reference is not None:

                provision_label = (
                    "Clause"
                    if document_type == "bill"
                    else "Section"
                )

                context_lines.append(
                    f"{provision_label}: {provision_reference}"
                )

            if section_title:
                context_lines.append(
                    f"Section Title: {section_title}"
                )

            if (
                subsection_number is not None
                and subsection_total_parts > 1
            ):
                context_lines.append(
                    f"Subsection Part: "
                    f"{subsection_part}/{subsection_total_parts}"
                )

            if case_name:
                context_lines.append(
                    f"Case: {case_name}"
                )

            context_lines.extend([
                "",
                "Content:",
                content
            ])

            context_parts.append(
                "\n".join(context_lines)
            )

            # 6. Retrieval debugging
            similarity_display = (
                f"{similarity:.4f}"
                if similarity is not None
                else "N/A"
            )

            print(
                f"[Source {index}] "
                f"Chunk={chunk_id} | "
                f"{page_label}={page_display} | "
                f"Provision={provision_reference} | "
                f"Similarity={similarity_display}"
            )

        return {
            "context": "\n\n".join(context_parts),
            "sources": sources,
            "retrieval_performance": retrieval_performance
        }

    def build_context(
        self,
        query: str,
        document_id: str | None = None,
        user_id: str | None = None
    ) -> str:

        payload = self.build_context_payload(
            query=query,
            document_id=document_id,
            user_id=user_id
        )

        return payload["context"]