
from rag.embeddings.embedding_manager import EmbeddingManager
from rag.retrieve.search_repository import SearchRepository
from rag.retrieve.mmr import cosine_similarity
embedding_manager = EmbeddingManager()
search_repository = SearchRepository()

question = "What is the basic structure doctrine of the Indian Constitution?"

query_embedding = embedding_manager.generate_embedding(question)


# Baseline: ordinary vector search
normal_results = search_repository.search(
    query_embedding=query_embedding,
    match_count=5
)


# MMR: retrieve 20 candidates and select diverse Top-5
mmr_results = search_repository.search_with_mmr(
    query_embedding=query_embedding,
    candidate_count=20,
    top_k=5,
    lambda_param=0.7
)


def display_results(title, results):

    print(f"\n{'=' * 65}")
    print(title)
    print('=' * 65)

    for index, result in enumerate(results, start=1):

        print(f"\n--- Result {index} ---")
        print("Chunk ID:", result["chunk_id"])
        print("Similarity:", round(result["similarity"], 4))
        print("Content:", result["content"])


display_results("NORMAL VECTOR SEARCH", normal_results)
display_results("MMR SEARCH", mmr_results)


for lambda_value in [0.7, 0.5, 0.3]:

    results = search_repository.search_with_mmr(
        query_embedding=query_embedding,
        candidate_count=20,
        top_k=5,
        lambda_param=lambda_value
    )

    print(f"\n========== MMR lambda = {lambda_value} ==========")

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. {result['chunk_id']} | "
            f"Similarity: {result['similarity']:.4f}"
        )
        print(result["content"][:250])
        print()


results = search_repository.search_with_mmr(
    query_embedding=query_embedding,
    candidate_count=20,
    top_k=5,
    lambda_param=0.7
)

print("\nPairwise similarity between retrieved chunks:\n")

for i in range(len(results)):
    for j in range(i + 1, len(results)):
        similarity = cosine_similarity(
            results[i]["embedding"],
            results[j]["embedding"]
        )

        print(
            f"{results[i]['chunk_id']} vs "
            f"{results[j]['chunk_id']}: {similarity:.4f}"
        )