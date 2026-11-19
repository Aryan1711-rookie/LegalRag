
from rag.retrieve.retrieval_service import RetrievalService


class RetrievalRunner:

    def __init__(self):
        self.retrieval_service = RetrievalService()

    def retrieve(
        self,
        question: str,
        document_id: str | None = None,
        top_k: int = 5
    ) -> list[dict]:

        return self.retrieval_service.retrieve(
            question=question,
            document_id=document_id,
            top_k=top_k
        )

    def get_retrieved_chunk_ids(
        self,
        question: str,
        document_id: str | None = None,
        top_k: int = 5
    ) -> list[str]:

        chunks = self.retrieve(
            question=question,
            document_id=document_id,
            top_k=top_k
        )

        return [
            chunk["chunk_id"]
            for chunk in chunks
            if chunk.get("chunk_id")
        ]
