import argparse
import json

from rag.retrieve.search_repository import SearchRepository
from rag.embeddings.embedding_manager import EmbeddingManager


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--document-id", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--question", required=True)

    args = parser.parse_args()

    repository = SearchRepository()
    embedding_manager = EmbeddingManager()

    query_embedding = embedding_manager.generate_embedding(
        args.question
    )

    chunks, performance = repository.search_hybrid_with_metrics(
        question=args.question,
        query_embedding=query_embedding,
        document_id=args.document_id,
        user_id=args.user_id,
        candidate_count=20,
        top_k=5
    )

    print("\n========== RETRIEVED CHUNKS ==========")

    for chunk in chunks:

        metadata = chunk.get("metadata") or {}

        print("\nChunk:", chunk["chunk_id"])
        print("Section:", metadata.get("section_number"))
        print("Title:", metadata.get("section_title"))
        print("RRF score:", chunk["rrf_score"])
        print("Content:", chunk["content"][:250])

    print("\n========== PERFORMANCE ==========")

    print(json.dumps(performance, indent=2))


if __name__ == "__main__":
    main()