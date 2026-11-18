
from rag.retrieve.retrieval_service import RetrievalService
from rag.generation.context_builder import ContextBuilder
from rag.generation.generation_service import GenerationService


class RAGService:

    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.context_builder = ContextBuilder(self.retrieval_service)
        self.generation_service = GenerationService(self.context_builder)

    def answer_question(
        self,
        question: str,
        document_id: str | None = None
    ):
        return self.generation_service.generate_response(
            prompt=question,
            document_id=document_id
        )
