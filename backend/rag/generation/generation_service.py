import os
from pathlib import Path

from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
from groq import Groq # pyright: ignore[reportMissingImports]

from rag.generation.citation_validator import CitationValidator
from rag.generation.grounding_validator import GroundingValidator

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL= os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-120b")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")
if not GROQ_MODEL:
    raise ValueError("GROQ_MODEL_NAME is missing in .env")

class GenerationService:
    def __init__(self, context_builder):
        self.model= GROQ_MODEL
        self.client = Groq(api_key=GROQ_API_KEY)
        self.context_builder = context_builder
        self.citation_validator = CitationValidator()
        self.grounding_validator = GroundingValidator(
        client=self.client,
        model=self.model
        )
    def generate_response(self, prompt: str, document_id: str | None = None) -> dict:
        # Step 1: Build context
        #context = self.context_builder.build_context(prompt)
        
        # Step 1: Build context and trusted source registry
        
        context_payload = self.context_builder.build_context_payload(prompt, document_id=document_id)

        context = context_payload["context"]
        sources = context_payload["sources"]
        
        # Step 2: Create a structured prompt
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

        # Step 4: Extract generated answer
        answer = completion.choices[0].message.content
        citation_report = self.citation_validator.validate(
    answer=answer,
    sources=sources
)
        grounding_report = self.grounding_validator.validate(
    answer=answer,
    sources=sources
)

        return {
            "question": prompt,
            "answer": answer,
            "model": self.model,
            "context": context,
            "sources": sources,
            "citation_report": citation_report,
            "grounding_report": grounding_report
        }





