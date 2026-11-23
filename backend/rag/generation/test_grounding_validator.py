
# from rag.retrieve.retrieval_service import RetrievalService
# from rag.generation.context_builder import ContextBuilder
# from rag.generation.grounding_validator import GroundingValidator
# from rag.generation.generation_service import GenerationService


# # Step 1: Initialize existing RAG components
# retrieval_service = RetrievalService()
# context_builder = ContextBuilder(retrieval_service)

# generation_service = GenerationService(context_builder)


# # Step 2: Retrieve actual legal evidence
# question = "What is the basic structure doctrine of the Indian Constitution?"

# context_payload = context_builder.build_context_payload(question)

# sources = context_payload["sources"]


# # Step 3: Create test answer
# test_answer = """
# The Kesavananda Bharati case examined whether Parliament
# could amend any part of the Constitution and what limits
# exist on that power. [Source 3, Page 12]

# The Supreme Court struck down Clause (4) of Article 329-A
# in the Indira Nehru Gandhi case. [Source 4, Page 13]

# The Kesavananda Bharati judgment explicitly declared that
# the Constitution contains exactly five essential features.
# [Source 3, Page 12]

# The Minerva Mills case involved a challenge to provisions
# of the 42nd Amendment concerning judicial review and
# Parliament's amendment powers. [Source 5, Page 14]
# """


# # Step 4: Initialize grounding evaluator
# grounding_validator = GroundingValidator(
#     client=generation_service.client,
#     model=generation_service.model
# )


# # Step 5: Evaluate claims
# result = grounding_validator.validate(
#     answer=test_answer,
#     sources=sources
# )


# # Step 6: Display results
# print("\n========== GROUNDING EVALUATION ==========\n")

# print("Overall assessment:", result["overall_assessment"])
# print("Total claims:", result["total_claims"])
# print("Supported:", result["supported_claims"])
# print("Partially supported:", result["partially_supported_claims"])
# print("Unsupported:", result["unsupported_claims"])

# print("\n========== INDIVIDUAL CLAIMS ==========\n")

# for index, claim in enumerate(result["claims"], start=1):

#     print(f"\nClaim {index}: {claim['claim']}")
#     print("Status:", claim["status"])
#     print("Cited sources:", claim["cited_sources"])
#     print("Supporting evidence:", claim["supporting_evidence"])
#     print("Explanation:", claim["explanation"])

#     if claim["unknown_sources"]:
#         print("Unknown sources:", claim["unknown_sources"])



import os
import json

from dotenv import load_dotenv
from groq import Groq

from rag.generation.grounding_validator import GroundingValidator


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

model = os.getenv("GROUNDING_MODEL_NAME") or os.getenv(
    "GROQ_MODEL_NAME",
    "openai/gpt-oss-120b"
)

validator = GroundingValidator(
    client=client,
    model=model
)

# Controlled test evidence
sources = [
    {
        "source": 1,
        "document": "BNSS2023.pdf",
        "document_type": "act",
        "page": 126,
        "section_number": "187",
        "chunk_id": "chunk_00733",
        "content": (
            "into consideration whether such person has not "
            "been released on bail or his bail has been "
            "cancelled, authorise, from time to time, the "
            "detention of the accused in such custody as "
            "such Magistrate thinks fit, for a term not "
            "exceeding fifteen days in the whole, or in "
            "parts, at any time during the initial forty "
            "days or sixty days out of detention period "
            "of sixty days or ninety days"
        )
    },
    {
        "source": 2,
        "document": "BNSS2023.pdf",
        "document_type": "act",
        "page": 126,
        "section_number": "187",
        "chunk_id": "chunk_00735",
        "content": (
            "(3) The Magistrate may authorise the detention "
            "of the accused person, beyond the period of "
            "fifteen days, if he is satisfied that adequate "
            "grounds exist for doing so, but no Magistrate "
            "shall authorise the detention of the accused "
            "person in custody under this sub-section for "
            "a total period exceeding— (i) ninety days, "
            "where the investigation relates to an offence "
            "punishable with death, imprisonment for life "
            "or imprisonment for a term of ten years or"
        )
    },
    {
        "source": 3,
        "document": "BNSS2023.pdf",
        "document_type": "act",
        "page": 126,
        "section_number": "187",
        "chunk_id": "chunk_00736",
        "content": (
            "for life or imprisonment for a term of ten "
            "years or more; (ii) sixty days, where the "
            "investigation relates to any other offence, "
            "and, on the expiry of the said period of "
            "ninety days, or sixty days, as the case may "
            "be, the accused person shall be released "
            "on bail if he is prepared to and does "
            "furnish bail"
        )
    }
]

sources.append({
    "source": 4,
    "document": "BNSS2023.pdf",
    "document_type": "act",
    "page": 126,
    "section_number": "187",
    "chunk_id": "chunk_00738",
    "content": (
        "(4) No Magistrate shall authorise detention "
        "of the accused in custody of the police "
        "under this section unless the accused is "
        "produced before him in person for the "
        "first time and subsequently every time "
        "till the accused remains in the custody "
        "of the police, but the Magistrate may "
        "extend further detention in judicial "
        "custody on production of the accused "
        "either in person or through the "
        "audio-video electronic means."
    )
})
test_cases = [
    {
        "name": "Correct police custody limit",
        "answer": (
            "Police custody cannot exceed fifteen "
            "days in aggregate. [Source 1, Page 126]"
        ),
        "expected": "SUPPORTED"
    },
    {
        "name": "Incorrect police custody limit",
        "answer": (
            "Police custody may extend to ninety "
            "days. [Source 2, Page 126]"
        ),
        "expected": "UNSUPPORTED"
    },
    {
        "name": "Incorrect citation",
        "answer": (
            "Police custody cannot exceed fifteen "
            "days. [Source 1, Page 999]"
        ),
        "expected": "UNSUPPORTED"
    },
    {
        "name": "Missing citation",
        "answer": (
            "Police custody cannot exceed fifteen days."
        ),
        "expected": "UNSUPPORTED"
    }
]
test_cases.extend([
    {
        "name": "Incorrect limit with surrounding statutory context",
        "answer": (
            "Police custody may extend to ninety days. "
            "[Source 1, Page 126]"
            "[Source 2, Page 126]"
            "[Source 3, Page 126]"
            "[Source 4, Page 126]"
        ),
        "expected": "UNSUPPORTED"
    },
    {
        "name": "Correct distinction between custody limits",
        "answer": (
            "Police custody is limited to fifteen days "
            "in aggregate, while the overall statutory "
            "detention period is sixty or ninety days, "
            "depending on the offence. "
            "[Source 1, Page 126]"
            "[Source 2, Page 126]"
            "[Source 3, Page 126]"
            "[Source 4, Page 126]"
        ),
        "expected": "SUPPORTED"
    }
])
passed = 0

for test in test_cases:

    print("\n========== TEST ==========")
    print("Name:", test["name"])

    report = validator.validate(
        answer=test["answer"],
        sources=sources
    )

    actual = report["overall_assessment"]

    success = actual == test["expected"]

    print("Expected:", test["expected"])
    print("Actual:", actual)
    print("Result:", "PASS" if success else "FAIL")

    print(json.dumps(
        report,
        indent=2,
        ensure_ascii=False
    ))

    passed += int(success)

print("\n========== SUMMARY ==========")

print("Passed:", passed)
print("Total:", len(test_cases))

print(
    f"Accuracy: "
    f"{passed / len(test_cases) * 100:.2f}%"
)

assert passed == len(test_cases), (
    "Grounding regression tests failed."
)