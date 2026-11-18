
from rag.retrieve.retrieval_service import RetrievalService
from rag.generation.context_builder import ContextBuilder
from rag.generation.grounding_validator import GroundingValidator
from rag.generation.generation_service import GenerationService


# Step 1: Initialize existing RAG components
retrieval_service = RetrievalService()
context_builder = ContextBuilder(retrieval_service)

generation_service = GenerationService(context_builder)


# Step 2: Retrieve actual legal evidence
question = "What is the basic structure doctrine of the Indian Constitution?"

context_payload = context_builder.build_context_payload(question)

sources = context_payload["sources"]


# Step 3: Create test answer
test_answer = """
The Kesavananda Bharati case examined whether Parliament
could amend any part of the Constitution and what limits
exist on that power. [Source 3, Page 12]

The Supreme Court struck down Clause (4) of Article 329-A
in the Indira Nehru Gandhi case. [Source 4, Page 13]

The Kesavananda Bharati judgment explicitly declared that
the Constitution contains exactly five essential features.
[Source 3, Page 12]

The Minerva Mills case involved a challenge to provisions
of the 42nd Amendment concerning judicial review and
Parliament's amendment powers. [Source 5, Page 14]
"""


# Step 4: Initialize grounding evaluator
grounding_validator = GroundingValidator(
    client=generation_service.client,
    model=generation_service.model
)


# Step 5: Evaluate claims
result = grounding_validator.validate(
    answer=test_answer,
    sources=sources
)


# Step 6: Display results
print("\n========== GROUNDING EVALUATION ==========\n")

print("Overall assessment:", result["overall_assessment"])
print("Total claims:", result["total_claims"])
print("Supported:", result["supported_claims"])
print("Partially supported:", result["partially_supported_claims"])
print("Unsupported:", result["unsupported_claims"])

print("\n========== INDIVIDUAL CLAIMS ==========\n")

for index, claim in enumerate(result["claims"], start=1):

    print(f"\nClaim {index}: {claim['claim']}")
    print("Status:", claim["status"])
    print("Cited sources:", claim["cited_sources"])
    print("Supporting evidence:", claim["supporting_evidence"])
    print("Explanation:", claim["explanation"])

    if claim["unknown_sources"]:
        print("Unknown sources:", claim["unknown_sources"])
