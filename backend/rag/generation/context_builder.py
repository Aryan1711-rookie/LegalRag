
class ContextBuilder:

    def __init__(self, retrieval_service):
        self.retrieval_service = retrieval_service

    def build_context_payload(
        self,
        query: str,
        document_id: str | None = None
    ) -> dict:

        retrieved_docs, retrieval_performance = (
            self.retrieval_service.retrieve_with_metrics(
                question=query,
                document_id=document_id
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

        for index, doc in enumerate(retrieved_docs, start=1):
            metadata = doc.get("metadata", {})
            chunk_id = doc.get("chunk_id", "Unknown")
            content = doc.get("content", "")
            similarity = doc.get("similarity", 0)
            source = metadata.get("source", "Unknown source")
            page_number = metadata.get("page_number", "Unknown")

            sources.append({
                "source": index,
                "document": source,
                "page": page_number,
                "chunk_id": chunk_id,
                "content": content
            })

            context_part = f"""
[Source {index}]
Chunk ID: {chunk_id}
Document: {source}
Page: {page_number}
Similarity: {similarity:.4f}

Content:
{content}
"""

            context_parts.append(context_part.strip())

        return {
            "context": "\n\n".join(context_parts),
            "sources": sources,
            "retrieval_performance": retrieval_performance
        }

    def build_context(self, query: str) -> str:
        payload = self.build_context_payload(query)
        return payload["context"]
