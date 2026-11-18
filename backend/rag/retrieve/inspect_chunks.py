
from rag.retrieve.search_repository import SearchRepository
from rag.embeddings.embedding_manager import EmbeddingManager

embedding_manager = EmbeddingManager()
repository = SearchRepository()

query = "What is the Basic Structure Doctrine of the Indian Constitution?"

query_embedding = embedding_manager.generate_embedding(query)

chunks = repository.search(
    query_embedding=query_embedding,
    match_count=30
)

target_ids = {
    "chunk_00026",
    "chunk_00027",
    "chunk_00028",
    "chunk_00030"
}

for chunk in chunks:
    if chunk["chunk_id"] in target_ids:
        print("\n" + "=" * 80)
        print("CHUNK:", chunk["chunk_id"])
        print("METADATA:", chunk.get("metadata", {}))
        print("CONTENT:")
        print(chunk["content"])
