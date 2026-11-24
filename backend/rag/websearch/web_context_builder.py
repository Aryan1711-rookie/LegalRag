
import re
from urllib.parse import urlparse


class WebContextBuilder:
    """
    Convert Tavily results into source-backed evidence
    for LegalMind's web research generation pipeline.
    """

    def __init__(
        self,
        max_sources: int = 6,
        max_chars_per_source: int = 1800,
        max_context_chars: int = 10000,
    ):
        self.max_sources = max_sources
        self.max_chars_per_source = max_chars_per_source
        self.max_context_chars = max_context_chars

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\s+", " ", text or "")
        return text.strip()

    @staticmethod
    def _is_index_page(url: str) -> bool:
        path = urlparse(url).path.lower().rstrip("/")

        index_paths = {
            "/latest-orders",
            "/latest-updates",
            "/cause-list",
            "/landmark-judgment-summaries",
        }

        return path in index_paths

    @staticmethod
    def _is_judgment_document(source: dict) -> bool:
        url = source.get("url", "")
        path = urlparse(url).path.lower()

        if source.get("is_judgment_pdf"):
            return True

        if "sci-get-pdf" in path:
            return True

        return False

    def build(
        self,
        results: list[dict],
        judgments_only: bool = False,
    ) -> dict:
        selected = []

        for source in results:
            if len(selected) >= self.max_sources:
                break

            url = source.get("url", "")

            if self._is_index_page(url):
                continue

            if judgments_only and not self._is_judgment_document(source):
                continue

            content = self._clean_text(
                source.get("content", "")
            )

            if not content:
                continue

            selected.append({
                "source_id": len(selected) + 1,
                "title": source.get("title", ""),
                "url": url,
                "content": content[:self.max_chars_per_source],
                "published_date": source.get("published_date"),
                "official_source": source.get("official_source", False),
                "source_type": source.get("source_type", "web_page"),
            })

        context_blocks = []
        included_sources = []
        used_chars = 0

        for source in selected:
            block = (
                f"[Source {source['source_id']}]\n"
                f"Title: {source['title']}\n"
                f"URL: {source['url']}\n"
                f"Content: {source['content']}\n"
            )

            if used_chars + len(block) > self.max_context_chars:
                break

            context_blocks.append(block)
            included_sources.append(source)
            used_chars += len(block)

        return {
            "context": "\n\n".join(context_blocks),
            "sources": included_sources,
            "source_count": len(included_sources),
            "context_characters": used_chars,
        }
