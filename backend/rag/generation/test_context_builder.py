
from rag.retrieve.retrieval_service import RetrievalService
from rag.generation.context_builder import ContextBuilder

retrieval_service = RetrievalService()
context_builder = ContextBuilder(retrieval_service)

question = "What is the basic structure doctrine of the Indian Constitution?"

result = context_builder.build_context_payload(question)

print("\n========== GENERATED CONTEXT ==========\n")
print(result["context"])

print("\n========== TRUSTED SOURCE REGISTRY ==========\n")

for source in result["sources"]:
    print(source)
