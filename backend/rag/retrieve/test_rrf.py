from rag.retrieve.rrf import reciprocal_rank_fusion


dense_results = [
    {"id": "A", "similarity": 0.92},
    {"id": "B", "similarity": 0.89},
    {"id": "C", "similarity": 0.85}
]

lexical_results = [
    {"id": "B", "lexical_score": 0.49},
    {"id": "D", "lexical_score": 0.41},
    {"id": "E", "lexical_score": 0.35}
]

results = reciprocal_rank_fusion(
    dense_results,
    lexical_results
)

print("\n========== RRF RESULTS ==========")

for rank, chunk in enumerate(results, start=1):

    print(
        f"Rank: {rank} | "
        f"Chunk: {chunk['id']} | "
        f"RRF Score: {chunk['rrf_score']:.6f}"
    )

assert results[0]["id"] == "B"
assert len(results) == 5
assert reciprocal_rank_fusion([], []) == []

print("\nAll tests passed.")