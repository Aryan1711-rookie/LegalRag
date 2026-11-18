
from rag.retrieve.retrieval_service import RetrievalService

retrieval_service = RetrievalService()

DOCUMENT_A_ID = "81dd79c3-d586-4b22-b82e-14c79c1dc84d"
DOCUMENT_B_ID = "ffd096c8-da87-4aa4-85ad-a90a477be4ab"

question1 = "What is the Basic Structure Doctrine of the Indian Constitution?"
question2 = "What were the facts, legal issues, and final judgment in the Nirbhaya case?"
# Test A: Retrieve only from Document A
results_a = retrieval_service.retrieve(
    question=question1,
    document_id=DOCUMENT_A_ID
)

# Test B: Retrieve only from Document B
results_b = retrieval_service.retrieve(
    question=question2,
    document_id=DOCUMENT_B_ID
)

print("\n========== DOCUMENT A ==========")
for chunk in results_a:
    print(chunk["document_id"], chunk["chunk_id"])

print("\n========== DOCUMENT B ==========")
for chunk in results_b:
    print(chunk["document_id"], chunk["chunk_id"])

# Verify isolation
assert all(
    str(chunk["document_id"]) == DOCUMENT_A_ID
    for chunk in results_a
), "Document A returned chunks from another document!"

assert all(
    str(chunk["document_id"]) == DOCUMENT_B_ID
    for chunk in results_b
), "Document B returned chunks from another document!"

print("\nSUCCESS: Document isolation verified.")


INVALID_DOCUMENT_ID = "00000000-0000-0000-0000-000000000000"

results_invalid = retrieval_service.retrieve(
    question=question1,
    document_id=INVALID_DOCUMENT_ID
)

print("\n========== INVALID DOCUMENT ==========")
print("Retrieved chunks:", len(results_invalid))

assert len(results_invalid) == 0, (
    "Invalid document ID unexpectedly returned results!"
)

print("SUCCESS: Invalid document ID returns zero results.")
