
from rag.retrieve.retrieval_service import RetrievalService
from rag.generation.context_builder import ContextBuilder
from rag.generation.generation_service import GenerationService

# Initialize the complete pipeline
retrieval_service = RetrievalService()
context_builder = ContextBuilder(retrieval_service)
generation_service = GenerationService(context_builder)

# Test question
question = (
    "What did the Supreme Court decide about cryptocurrency taxation in India in 2024?"
)

print("\n" + "=" * 70)
print("QUESTION")
print("=" * 70)
print(question)

# Run complete pipeline
result = generation_service.generate_response(question)

print("\n" + "=" * 70)
print("GENERATED ANSWER")
print("=" * 70)
print(result["answer"])

print("\n" + "=" * 70)
print("CITATION VALIDATION")
print("=" * 70)
print(result["citation_report"])

print("\n" + "=" * 70)
print("GROUNDING VALIDATION")
print("=" * 70)
print(result["grounding_report"])

print("\n" + "=" * 70)
print("RETRIEVED SOURCES")
print("=" * 70)

for source in result["sources"]:
    print(
        f"Source {source['source']} | "
        f"Page {source['page']} | "
        f"Chunk {source['chunk_id']}"
    )

print("\nPipeline execution completed.")
