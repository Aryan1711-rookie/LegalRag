
from evaluation.metrics.retrieval import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)

from evaluation.metrics.answer_quality import (
    AnswerQualityEvaluator,
)


class Evaluator:

    def __init__(self, client=None, model=None):
        self.answer_quality_evaluator = None

        if client is not None and model is not None:
            self.answer_quality_evaluator = AnswerQualityEvaluator(
                client=client,
                model=model
            )

    def evaluate_retrieval(
        self,
        retrieved_chunks: list[str],
        relevant_chunks: list[str],
        k: int = 5
    ):
        if not relevant_chunks:
            raise ValueError(
                "Cannot evaluate retrieval without relevant chunk IDs."
            )

        return {
            f"precision@{k}": precision_at_k(
                retrieved_chunks, relevant_chunks, k
            ),
            f"recall@{k}": recall_at_k(
                retrieved_chunks, relevant_chunks, k
            ),
            "mrr": reciprocal_rank(
                retrieved_chunks, relevant_chunks
            ),
            f"ndcg@{k}": ndcg_at_k(
                retrieved_chunks, relevant_chunks, k
            )
        }

    def evaluate_answer(
    self,
    question: str,
    answer: str,
    ground_truth: str,
    key_points: list[str],
    context: str
):
        if self.answer_quality_evaluator is None:
            raise RuntimeError(
                "Answer quality evaluator has not been initialized."
            )

        return self.answer_quality_evaluator.evaluate(
            question=question,
            answer=answer,
            ground_truth=ground_truth,
            key_points=key_points,
            context=context
        )
