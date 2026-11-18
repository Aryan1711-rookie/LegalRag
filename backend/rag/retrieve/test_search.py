
from rag.embeddings.embedding_manager import EmbeddingManager
from rag.retrieve.search_repository import SearchRepository

# Initialize components
embedding_manager = EmbeddingManager()
search_repository = SearchRepository()

# User's test question
question = "What is the basic structure doctrine of the Indian Constitution?"

# Generate query embedding
query_embedding = embedding_manager.generate_embedding(question)

# Retrieve relevant chunks
results = search_repository.search(
    query_embedding=query_embedding,
    match_count=10
)

filtered_results = [
    result for result in results
    if result["similarity"] >= 0.70
] 

# Display results
print("\nQuestion:", question)
print("\nRetrieved Chunks:\n")

for index, result in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print("Chunk ID:", result["chunk_id"])
    print("Similarity:", round(result["similarity"], 4))
    print("Content:", result["content"])
