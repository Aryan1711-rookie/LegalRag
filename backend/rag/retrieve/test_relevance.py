
from rag.embeddings.embedding_manager import EmbeddingManager
from rag.retrieve.search_repository import SearchRepository

embedding_manager = EmbeddingManager()
search_repository = SearchRepository()

questions = [
    "What is the Basic Structure Doctrine?",
    "What happened in Minerva Mills?",
    "What did the Supreme Court decide about cryptocurrency taxation in India in 2024?"
]

for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    query_embedding = embedding_manager.generate_embedding(question)

    # Ordinary vector search
    vector_results = search_repository.search(
        query_embedding=query_embedding,
        match_count=10
    )

    # Vector search followed by MMR
    mmr_results = search_repository.search_with_mmr(
        query_embedding=query_embedding,
        candidate_count=20,
        top_k=5,
        lambda_param=0.7
    )

    print("\n--- VECTOR SEARCH ---")

    for chunk in vector_results:
        print(
            f"{chunk['chunk_id']} | "
            f"Similarity: {chunk['similarity']:.4f}"
        )

    print("\n--- MMR SEARCH ---")

    for chunk in mmr_results:
        print(
            f"{chunk['chunk_id']} | "
            f"Similarity: {chunk['similarity']:.4f}"
        )
