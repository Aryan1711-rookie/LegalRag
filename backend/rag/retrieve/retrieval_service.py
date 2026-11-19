
from time import perf_counter

from rag.retrieve.search_repository import SearchRepository
from rag.embeddings.embedding_manager import EmbeddingManager


class RetrievalService:

    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.search_repository = SearchRepository()

    def retrieve_with_metrics(
        self,
        question: str,
        candidate_count: int = 20,
        top_k: int = 5,
        lambda_param: float = 0.7,
        document_id: str | None = None
    ):
        # 1. Generate query embedding
        embedding_start = perf_counter()

        query_embedding = self.embedding_manager.generate_embedding(
            question
        )

        embedding_seconds = perf_counter() - embedding_start

        # 2. Database search + MMR
        search_start = perf_counter()

        retrieved_chunks, search_performance = self.search_repository.search_with_mmr_and_metrics(
            query_embedding=query_embedding,
            candidate_count=candidate_count,
            top_k=top_k,
            document_id=document_id,
            lambda_param=lambda_param
        )

        search_seconds = perf_counter() - search_start

        performance = {
    "embedding_seconds": round(embedding_seconds, 4),
    "database_seconds": search_performance["database_seconds"],
    "mmr_seconds": search_performance["mmr_seconds"],
    "search_mmr_seconds": round(search_seconds, 4),
    "retrieval_total_seconds": round(
        embedding_seconds + search_seconds, 4
    ),
    "candidate_count": search_performance["candidate_count"],
    "selected_count": search_performance["selected_count"]
}

        return retrieved_chunks, performance

    def retrieve(
        self,
        question: str,
        candidate_count: int = 20,
        top_k: int = 5,
        lambda_param: float = 0.7,
        document_id: str | None = None
    ):
        retrieved_chunks, _ = self.retrieve_with_metrics(
            question=question,
            candidate_count=candidate_count,
            top_k=top_k,
            lambda_param=lambda_param,
            document_id=document_id
        )

        return retrieved_chunks
