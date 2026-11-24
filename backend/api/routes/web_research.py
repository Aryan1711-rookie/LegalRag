
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from rag.websearch.tavily_search import TavilySearchService
from rag.websearch.web_context_builder import WebContextBuilder
from rag.websearch.web_generation import WebGenerationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/web-research",
    tags=["Web Research"],
)


class WebResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)


@router.post("/search")
async def web_research(request: WebResearchRequest):
    try:
        search = TavilySearchService()
        builder = WebContextBuilder()
        generator = WebGenerationService()

        results = await search.search(
            query=request.query,
            max_results=8,
            official_only=True,
        )

        prepared = builder.build(
            results,
            judgments_only=False,
        )

        generated = await generator.generate(
            query=request.query,
            prepared_context=prepared,
        )

        return {
            "answer": generated["answer"],
            "sources": [
                {
                    "source_id": source["source_id"],
                    "title": source["title"],
                    "url": source["url"],
                    "official_source": source.get(
                        "official_source", False
                    ),
                }
                for source in generated["sources"]
            ],
            "verification_status": "UNVERIFIED_WEB",
            "disclaimer": (
                "This answer uses external web sources "
                "and AI-generated analysis. Information "
                "may be incomplete, outdated or inaccurate. "
                "Verify legal conclusions against official "
                "judgments and legislation."
            ),
            "model": generated.get("model"),
        }

    except Exception:
        logger.exception("Web research failed")

        raise HTTPException(
            status_code=502,
            detail="Web research is temporarily unavailable.",
        )
