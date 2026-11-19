
import os
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from groq import Groq  # pyright: ignore[reportMissingImports]

from rag.generation.citation_validator import CitationValidator
from rag.generation.grounding_validator import GroundingValidator


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL_NAME",
    "openai/gpt-oss-120b"
)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")

if not GROQ_MODEL:
    raise ValueError("GROQ_MODEL_NAME is missing in .env")


class GenerationService:

    def __init__(self, context_builder):
        self.model = GROQ_MODEL
        self.client = Groq(api_key=GROQ_API_KEY)
        self.context_builder = context_builder

        self.citation_validator = CitationValidator()

        self.grounding_validator = GroundingValidator(
            client=self.client,
            model=self.model
        )

    def generate_response(
        self,
        prompt: str,
        document_id: str | None = None
    ) -> dict:

        # Start overall timer
        total_start = perf_counter()

        # Step 1: Build context and trusted source registry
        context_start = perf_counter()

        context_payload = self.context_builder.build_context_payload(
            prompt,
            document_id=document_id
        )

        context_build_time = perf_counter() - context_start
        retrieval_performance = context_payload.get(
                "retrieval_performance",
                 {}
            )

        context = context_payload["context"]
        sources = context_payload["sources"]

        # Step 2: Create structured system prompt
        structured_prompt = """
You are LegalRag, an AI legal research assistant
specialising in Indian law.

Your task is to answer questions using the supplied
legal document excerpts.

STRICT RULES:

1. Use the supplied context as your primary source.
2. Do not invent facts, case names, judgments,
   statutory provisions or legal citations.
3. Every factual legal claim must have a source citation.
4. Use ONLY this citation format:

   [Source 1, Page 13]

5. The source number and page number must exactly
   match the supplied context.
6. Never generate line numbers or external citation
   references that are not provided.
7. If information is missing from the context,
   explicitly state that it is not available.
8. Clearly distinguish between facts stated in the
   document and your own explanatory interpretation.
9. Do not claim that a judgment held something unless
   the supplied excerpt supports that claim.
10. If the supplied context is insufficient to answer
    the question, say so.
11. Do not treat a question, issue, or argument mentioned
    in a judgment as the final ruling of the Court.
12. Do not add legal principles from your general knowledge,
    even if they are legally correct, unless the supplied
    context explicitly supports them.
13. Clearly label any logical inference as an inference.
    Do not present an inference as a direct judicial finding.
14. If a source only mentions a case or legal issue,
    do not attribute a specific holding to that case.
15. Every citation must support the specific claim
    immediately preceding it.

Produce a clear, structured and legally precise answer.
"""

        # Step 3: Generate answer
        generation_start = perf_counter()

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": structured_prompt
                },
                {
                    "role": "user",
                    "content": f"""
Legal context:
{context}

Question:
{prompt}

Answer using the supplied legal context and cite
the relevant sources.
"""
                }
            ],
            temperature=0.2,
            max_tokens=1500
        )

        generation_time = perf_counter() - generation_start

        # Step 4: Extract generated answer
        answer = completion.choices[0].message.content

        # Step 5: Validate citations
        citation_start = perf_counter()

        citation_report = self.citation_validator.validate(
            answer=answer,
            sources=sources
        )

        citation_validation_time = perf_counter() - citation_start

        # Step 6: Validate grounding
        grounding_start = perf_counter()

        grounding_report = self.grounding_validator.validate(
            answer=answer,
            sources=sources
        )

        grounding_validation_time = perf_counter() - grounding_start

        # Step 7: Capture token usage
        usage = completion.usage

        token_usage = {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0
        }

        # Step 8: Collect performance metrics
        # Step 8: Collect performance metrics

        total_time = perf_counter() - total_start

        performance = {
            "context_build_seconds": round(context_build_time, 4),

            "embedding_seconds": retrieval_performance.get(
                "embedding_seconds", 0
            ),

            "search_mmr_seconds": retrieval_performance.get(
                "search_mmr_seconds", 0
            ),

            "retrieval_total_seconds": retrieval_performance.get(
                "retrieval_total_seconds", 0
            ),

            "generation_seconds": round(generation_time, 4),

            "citation_validation_seconds": round(
                citation_validation_time, 4
            ),

            "grounding_validation_seconds": round(
                grounding_validation_time, 4
            ),

            "total_seconds": round(total_time, 4),

            "token_usage": token_usage,
            "database_seconds": retrieval_performance.get(
            "database_seconds", 0
            ),
            "mmr_seconds": retrieval_performance.get(
                "mmr_seconds", 0
            ),
            "candidate_count": retrieval_performance.get(
                "candidate_count", 0
            ),
            "selected_count": retrieval_performance.get(
                "selected_count", 0
            ),
        }
        # Step 9: Return response
        return {
            "question": prompt,
            "answer": answer,
            "model": self.model,
            "context": context,
            "sources": sources,
            "citation_report": citation_report,
            "grounding_report": grounding_report,
            "performance": performance
        }
