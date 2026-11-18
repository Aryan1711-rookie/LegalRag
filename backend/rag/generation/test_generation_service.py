
from rag.retrieve.retrieval_service import RetrievalService
from rag.generation.context_builder import ContextBuilder
from rag.generation.generation_service import GenerationService


# Initialize components
retrieval_service = RetrievalService()

context_builder = ContextBuilder(
    retrieval_service=retrieval_service
)

generation_service = GenerationService(
    context_builder=context_builder
)

# Ask a legal question
question = "What is the basic structure doctrine of the Indian Constitution?"

# Generate answer
result = generation_service.generate_response(question)

print("\n========== LEGALRAG ANSWER ==========\n")
print(result["answer"])

print("\n========== MODEL ==========\n")
print(result["model"])

print("\n========== TRUSTED SOURCES ==========\n")

for source in result["sources"]:
    print(source)

print("\n========== CITATION VALIDATION ==========\n")
print(result["citation_report"])