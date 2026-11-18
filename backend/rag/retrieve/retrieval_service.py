
from rag.retrieve.search_repository import SearchRepository
from rag.embeddings.embedding_manager import EmbeddingManager


class RetrievalService:

    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.search_repository = SearchRepository()

    def retrieve(
        self,
        question: str,
        candidate_count: int = 20,
        top_k: int = 5,
        lambda_param: float = 0.7,
        document_id: str | None= None
    ):

        # Step 1: Generate query embedding
        query_embedding = self.embedding_manager.generate_embedding(
            question
        )

        # Step 2: Retrieve relevant chunks using MMR
        retrieved_chunks = self.search_repository.search_with_mmr(
            query_embedding=query_embedding,
            candidate_count=candidate_count,
            top_k=top_k,
            document_id=document_id,
            lambda_param=lambda_param
        )

        # Step 3: Return retrieved context
        return retrieved_chunks
