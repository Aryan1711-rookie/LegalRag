
from rag.embeddings.embedding_manager import EmbeddingManager
from rag.retrieve.search_repository import SearchRepository
from rag.retrieve.reranker import CrossEncoderReranker


embedding_manager = EmbeddingManager()
search_repository = SearchRepository()
reranker = CrossEncoderReranker()


questions = [
    "What is the Basic Structure Doctrine?",
    "What happened in Minerva Mills?",
    "What did the Supreme Court decide about cryptocurrency taxation in India in 2024?"
]


for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:", question)
    print("=" * 80)

    # Step 1: Generate query embedding
    query_embedding = embedding_manager.generate_embedding(question)

    # Step 2: Retrieve candidates using BGE
    candidates = search_repository.search(
        query_embedding=query_embedding,
        match_count=10
    )

    print("\n--- BGE VECTOR SEARCH ---")

    for index, chunk in enumerate(candidates, start=1):
        print(
            f"{index}. {chunk['chunk_id']} | "
            f"BGE Similarity: {chunk['similarity']:.4f}"
        )

    # Step 3: Rerank candidates using Cross-Encoder
    reranked_chunks = reranker.rerank(
        query=question,
        documents=candidates,
        top_k=10
    )

    print("\n--- CROSS-ENCODER RERANKING ---")

    for index, chunk in enumerate(reranked_chunks, start=1):
        print(
            f"{index}. {chunk['chunk_id']} | "
            f"Rerank Score: {chunk['rerank_score']:.4f}"
            f"\n   BGE Similarity: {chunk['similarity']:.4f}"
            f"\n   Content: {chunk['content'][:200]}"
        )

print("\nCross-encoder evaluation completed.")
