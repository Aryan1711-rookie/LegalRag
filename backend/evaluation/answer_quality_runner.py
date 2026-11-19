
from services.rag_service import RAGService
from evaluation.evaluator import Evaluator


class AnswerQualityRunner:

    def __init__(self, document_id: str):
        self.document_id = document_id

        self.rag_service = RAGService()

        generation_service = self.rag_service.generation_service

        self.evaluator = Evaluator(
            client=generation_service.client,
            model=generation_service.model
        )

    def evaluate_case(self, case: dict) -> dict:

        # Generate an answer using the actual RAG pipeline
        response = self.rag_service.answer_question(
            question=case["question"],
            document_id=self.document_id
        )

        # Evaluate generated answer
        quality_metrics = self.evaluator.evaluate_answer(
            question=case["question"],
            answer=response["answer"],
            ground_truth=case["ground_truth"],
            key_points=case["key_points"],
            context=response["context"]
        )

        return {
            "id": case["id"],
            "question": case["question"],
            "answer": response["answer"],
            "quality_metrics": quality_metrics,
            "citation_report": response["citation_report"],
            "grounding_report": response["grounding_report"],
            "performance": response["performance"],
        }
