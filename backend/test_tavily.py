
import asyncio

from dotenv import load_dotenv

from rag.websearch.tavily_search import TavilySearchService
from rag.websearch.web_context_builder import WebContextBuilder

load_dotenv()


async def main():
    search_service = TavilySearchService()
    context_builder = WebContextBuilder()

    query = (
    "Supreme Court of India Article 324 "
    "appointment of Election Commissioners "
    "Anoop Baranwal Constitution Bench judgment"
)

    results = await search_service.search(
        query=query,
        max_results=8,
        official_only=True,
    )

    prepared = context_builder.build(
        results=results,
        judgments_only=True,
    )

    print("\n========== WEB CONTEXT ==========")
    print("Retrieved results:", len(results))
    print("Selected sources:", prepared["source_count"])
    print("Context characters:", prepared["context_characters"])

    for source in prepared["sources"]:
        print(
            f"\n[Source {source['source_id']}] "
            f"{source['title']}"
        )
        print(source["url"])

    print("\n========== CONTEXT PREVIEW ==========")
    print(prepared["context"][:3000])


if __name__ == "__main__":
    asyncio.run(main())
