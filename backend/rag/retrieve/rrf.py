def reciprocal_rank_fusion(
    dense_results: list[dict],
    lexical_results: list[dict],
    k: int = 60
) -> list[dict]:

    if k <= 0:
        raise ValueError("k must be positive.")

    scores = {}
    chunks = {}

    rankings = [
        ("dense", dense_results),
        ("lexical", lexical_results)
    ]

    for method, results in rankings:

        seen = set()

        for rank, chunk in enumerate(results, start=1):

            chunk_id = chunk["id"]

            if chunk_id in seen:
                continue

            seen.add(chunk_id)

            if chunk_id not in scores:
                scores[chunk_id] = 0.0
                chunks[chunk_id] = dict(chunk)

            scores[chunk_id] += 1 / (k + rank)

            if method == "dense":
                chunks[chunk_id]["dense_rank"] = rank
                chunks[chunk_id]["similarity"] = chunk.get(
                    "similarity"
                )

            else:
                chunks[chunk_id]["lexical_rank"] = rank
                chunks[chunk_id]["lexical_score"] = chunk.get(
                    "lexical_score"
                )

    fused_results = []

    for chunk_id, chunk in chunks.items():

        chunk["rrf_score"] = scores[chunk_id]

        fused_results.append(chunk)

    fused_results.sort(
        key=lambda chunk: (
            -chunk["rrf_score"],
            str(chunk["id"])
        )
    )

    return fused_results