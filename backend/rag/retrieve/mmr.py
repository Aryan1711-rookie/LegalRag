
import numpy as np


def cosine_similarity(a, b):
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def mmr(
    query_embedding,
    candidate_chunks,
    top_k=5,
    lambda_param=0.7
):
    selected = []
    remaining = list(range(len(candidate_chunks)))

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    while remaining and len(selected) < top_k:

        best_index = None
        best_score = float("-inf")

        for index in remaining:

            chunk_embedding = candidate_chunks[index]["embedding"]

            relevance = cosine_similarity(
                query_embedding,
                chunk_embedding
            )

            if selected:
                redundancy = max(
                    cosine_similarity(
                        chunk_embedding,
                        candidate_chunks[selected_index]["embedding"]
                    )
                    for selected_index in selected
                )
            else:
                redundancy = 0.0

            mmr_score = (
                lambda_param * relevance
                - (1 - lambda_param) * redundancy
            )

            if mmr_score > best_score:
                best_score = mmr_score
                best_index = index

        selected.append(best_index)
        remaining.remove(best_index)

    return [
        candidate_chunks[index]
        for index in selected
    ]
