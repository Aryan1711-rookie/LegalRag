
from evaluation.metrics.retrieval import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)


def test_retrieval_metrics():
    retrieved = ["chunk_1", "chunk_2", "chunk_3", "chunk_4"]
    relevant = ["chunk_2", "chunk_4"]

    precision = precision_at_k(retrieved, relevant, 4)
    recall = recall_at_k(retrieved, relevant, 4)
    mrr = reciprocal_rank(retrieved, relevant)
    ndcg = ndcg_at_k(retrieved, relevant, 4)

    print("Precision@4:", precision)
    print("Recall@4:", recall)
    print("MRR:", mrr)
    print("NDCG@4:", ndcg)


if __name__ == "__main__":
    test_retrieval_metrics()
