
import os
from urllib.parse import urlparse, urlunparse

from tavily import AsyncTavilyClient


class TavilySearchService:
    """
    Tavily-powered web retrieval for LegalMind AI.

    Features:
    - Indian legal source filtering
    - Official government and judicial source prioritization
    - URL deduplication
    - Judgment PDF detection
    - Structured results with stable source IDs
    """

    TRUSTED_DOMAINS = [
        "sci.gov.in",
        "api.sci.gov.in",
        "indiacode.nic.in",
        "egazette.gov.in",
        "nalsa.gov.in",
    ]

    EXCLUDED_DOMAINS = [
        "tavily.com",
        "bccourts.ca",
    ]

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise RuntimeError(
                "TAVILY_API_KEY is not configured."
            )

        self.client = AsyncTavilyClient(
            api_key=api_key
        )

    @staticmethod
    def _normalize_url(url: str) -> str:
        """
        Normalize URLs for deduplication.

        Removes fragments, normalizes the hostname,
        and strips trailing slashes.
        """
        parsed = urlparse(url)

        hostname = (parsed.hostname or "").lower()

        if not hostname:
            return ""

        scheme = parsed.scheme.lower()

        if scheme not in ("http", "https"):
            return ""

        port = f":{parsed.port}" if parsed.port else ""

        netloc = hostname + port

        path = parsed.path.rstrip("/") or "/"

        return urlunparse(
            (
                scheme,
                netloc,
                path,
                "",
                parsed.query,
                "",
            )
        )

    @classmethod
    def _is_official_source(cls, url: str) -> bool:
        """
        Determine whether a URL belongs to an
        approved Indian government or judicial domain.
        """
        hostname = (
            urlparse(url).hostname or ""
        ).lower()

        return any(
            hostname == domain
            or hostname.endswith("." + domain)
            for domain in cls.TRUSTED_DOMAINS
        )

    @staticmethod
    def _is_judgment_pdf(url: str) -> bool:
        """
        Identify likely judgment PDFs using URL patterns.

        This is a heuristic and does not establish
        authenticity or whether the decision was
        delivered by a Constitution Bench.
        """
        parsed = urlparse(url)

        path = parsed.path.lower()

        return (
            path.endswith(".pdf")
            and (
                "judgment" in path
                or "judgement" in path
            )
        )

    async def search(
        self,
        query: str,
        max_results: int = 8,
        official_only: bool = True,
    ) -> list[dict]:
        """
        Search web sources relevant to Indian legal research.

        Args:
            query:
                Natural-language legal research query.

            max_results:
                Maximum number of Tavily search results.

            official_only:
                Restrict results to approved official domains.

        Returns:
            List of structured web evidence sources.
        """

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty."
            )

        max_results = max(1, min(max_results, 20))

        options = {
            "query": query,
            "search_depth": "advanced",
            "topic": "general",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
            "exclude_domains": self.EXCLUDED_DOMAINS,
        }

        if official_only:
            options["include_domains"] = (
                self.TRUSTED_DOMAINS
            )

            # Restrict searches to official domains.
            # Tavily SDK versions may differ in whether
            # include_domains_mode is supported.
        else:
            options["country"] = "india"

        response = await self.client.search(
            **options
        )

        results = []
        seen_urls = set()

        for result in response.get("results", []):

            url = (result.get("url") or "").strip()
            content = (
                result.get("content") or ""
            ).strip()

            if not url or not content:
                continue

            normalized_url = self._normalize_url(url)

            if not normalized_url:
                continue

            if normalized_url in seen_urls:
                continue

            is_official = self._is_official_source(url)

            # Enforce official-source filtering locally,
            # even if the upstream search provider
            # returns an unexpected domain.
            if official_only and not is_official:
                continue

            hostname = (
                urlparse(url).hostname or ""
            ).lower()

            if any(
                hostname == domain
                or hostname.endswith("." + domain)
                for domain in self.EXCLUDED_DOMAINS
            ):
                continue

            seen_urls.add(normalized_url)

            results.append(
                {
                    "source_id": len(results) + 1,
                    "title": result.get("title", ""),
                    "url": url,
                    "content": content,
                    "score": result.get("score", 0),
                    "published_date": result.get(
                        "published_date"
                    ),
                    "official_source": is_official,
                    "is_judgment_pdf": (
                        self._is_judgment_pdf(url)
                    ),
                    "source_type": (
                        "judgment_pdf"
                        if self._is_judgment_pdf(url)
                        else "web_page"
                    ),
                }
            )

        return results
