
import math


def precision_at_k(retrieved, relevant, k):
    """
    Fraction of the top-k retrieved chunks that are relevant.
    """
    if k <= 0:
        raise ValueError("k must be greater than zero")

    retrieved_k = retrieved[:k]

    if not retrieved_k:
        return 0.0

    relevant_set = set(relevant)

    hits = sum(
        1 for chunk_id in retrieved_k
        if chunk_id in relevant_set
    )

    return hits / len(retrieved_k)


def recall_at_k(retrieved, relevant, k):
    """
    Fraction of all relevant chunks found in the top-k results.
    """
    if k <= 0:
        raise ValueError("k must be greater than zero")

    relevant_set = set(relevant)

    if not relevant_set:
        return 0.0

    retrieved_k = retrieved[:k]

    hits = sum(
        1 for chunk_id in retrieved_k
        if chunk_id in relevant_set
    )

    return hits / len(relevant_set)


def reciprocal_rank(retrieved, relevant):
    """
    Reciprocal rank of the first relevant retrieved chunk.
    """
    relevant_set = set(relevant)

    for rank, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant_set:
            return 1 / rank

    return 0.0


def ndcg_at_k(retrieved, relevant, k):
    """
    Normalized Discounted Cumulative Gain at k.
    Assumes binary relevance: relevant or irrelevant.
    """
    if k <= 0:
        raise ValueError("k must be greater than zero")

    relevant_set = set(relevant)

    if not relevant_set:
        return 0.0

    dcg = sum(
        1 / math.log2(rank + 1)
        for rank, chunk_id in enumerate(retrieved[:k], start=1)
        if chunk_id in relevant_set
    )

    ideal_hits = min(len(relevant_set), k)

    idcg = sum(
        1 / math.log2(rank + 1)
        for rank in range(1, ideal_hits + 1)
    )

    return dcg / idcg if idcg else 0.0
