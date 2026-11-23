from time import perf_counter

from rag.retrieve.search_repository import SearchRepository

from rag.embeddings.embedding_manager import EmbeddingManager

from rag.retrieve.section_expander import SectionExpander


class RetrievalService:

    def __init__(self):

        self.embedding_manager = EmbeddingManager()

        self.search_repository = SearchRepository()

        self.section_expander = SectionExpander(
            self.search_repository
        )

    def retrieve_with_metrics(
        self,
        question: str,
        candidate_count: int = 20,
        top_k: int = 5,
        lambda_param: float = 0.7,
        document_id: str | None = None,
        expand_sections: bool = True,
    ):

        # 1. Generate query embedding

        embedding_start = perf_counter()

        query_embedding = (
            self.embedding_manager.generate_embedding(
                question
            )
        )

        embedding_seconds = (
            perf_counter() - embedding_start
        )

        # 2. Database search + MMR

        search_start = perf_counter()

        retrieved_chunks, search_performance = (
            self.search_repository.search_with_mmr_and_metrics(
                query_embedding=query_embedding,
                candidate_count=candidate_count,
                top_k=top_k,
                document_id=document_id,
                lambda_param=lambda_param
            )
        )

        search_seconds = (
            perf_counter() - search_start
        )

        original_count = len(retrieved_chunks)

        # 3. Section-level context expansion

        expansion_start = perf_counter()

        if expand_sections:

            retrieved_chunks = self.section_expander.expand(
                question=question,
                retrieved_chunks=retrieved_chunks,
                document_id=document_id
            )

        expansion_seconds = (
            perf_counter() - expansion_start
        )

        # 4. Performance metrics

        performance = {
            "embedding_seconds": round(
                embedding_seconds, 4
            ),

            "database_seconds": search_performance[
                "database_seconds"
            ],

            "mmr_seconds": search_performance[
                "mmr_seconds"
            ],

            "search_mmr_seconds": round(
                search_seconds, 4
            ),

            "section_expansion_seconds": round(
                expansion_seconds, 4
            ),

            "retrieval_total_seconds": round(
                embedding_seconds
                + search_seconds
                + expansion_seconds,
                4
            ),

            "candidate_count": search_performance[
                "candidate_count"
            ],

            "selected_count": original_count,

            "expanded_count": len(retrieved_chunks),

            "additional_chunks": (
                len(retrieved_chunks) - original_count
            )
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

        retrieved_chunks, _ = (
            self.retrieve_with_metrics(
                question=question,
                candidate_count=candidate_count,
                top_k=top_k,
                lambda_param=lambda_param,
                document_id=document_id
            )
        )

        return retrieved_chunks

    def retrieve_hybrid_with_metrics(
    self,
    question: str,
    document_id: str,
    user_id: str,
    candidate_count: int = 20,
    top_k: int = 5,
    rrf_k: int = 60
):

        if not document_id or not user_id:
            raise ValueError(
                "Document ID and user ID are required."
            )

        total_start = perf_counter()

        # 1. Generate query embedding
        embedding_start = perf_counter()

        query_embedding = (
            self.embedding_manager.generate_embedding(
                question
            )
        )

        embedding_seconds = (
            perf_counter() - embedding_start
        )

        # 2. Hybrid retrieval (includes ownership check)
        retrieved_chunks, search_performance = (
            self.search_repository.search_hybrid_with_metrics(
                question=question,
                query_embedding=query_embedding,
                document_id=document_id,
                user_id=user_id,
                candidate_count=candidate_count,
                top_k=top_k,
                rrf_k=rrf_k
            )
        )

        original_count = len(retrieved_chunks)

        # 3. Section expansion
        expansion_start = perf_counter()

        if retrieved_chunks:
            retrieved_chunks = self.section_expander.expand(
                question=question,
                retrieved_chunks=retrieved_chunks,
                document_id=document_id
            )

        expansion_seconds = (
            perf_counter() - expansion_start
        )

        print("\n========== FINAL RETRIEVAL ==========")
        print("Before expansion:", original_count)
        print("After expansion:", len(retrieved_chunks))
        print("=====================================\n")

        # 4. Performance metrics
        performance = {
            **search_performance,
            "retrieval_strategy": "hybrid",

            "embedding_seconds": round(
                embedding_seconds, 4
            ),

            "section_expansion_seconds": round(
                expansion_seconds, 4
            ),

            "expanded_count": len(retrieved_chunks),

            "retrieval_total_seconds": round(
                perf_counter() - total_start, 4
            )
        }

        return retrieved_chunks, performance