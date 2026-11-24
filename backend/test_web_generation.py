
import asyncio
from dotenv import load_dotenv

from rag.websearch.tavily_search import TavilySearchService
from rag.websearch.web_context_builder import WebContextBuilder
from rag.websearch.web_generation import WebGenerationService

load_dotenv()


async def main():
    question = (
        "What did the Supreme Court hold in "
        "Anoop Baranwal regarding the appointment "
        "of Election Commissioners under Article 324?"
    )

    search = TavilySearchService()
    builder = WebContextBuilder()
    generator = WebGenerationService()

    results = await search.search(
        query=question,
        max_results=8,
        official_only=True,
    )

    context = builder.build(
        results,
        judgments_only=True,
    )

    response = await generator.generate(
        query=question,
        prepared_context=context,
    )

    print("\n========== WEB ANSWER ==========")
    print(response["answer"])

    print("\n========== VALIDATION ==========")
    print(response["verification_status"])
    print("Citation IDs:", response["citation_ids"])

    print("\n========== SOURCES ==========")
    for source in response["sources"]:
        print(
            f"[Source {source['source_id']}] "
            f"{source['title']}"
        )
        print(source["url"])


if __name__ == "__main__":
    asyncio.run(main())
