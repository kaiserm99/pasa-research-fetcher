"""Main fetcher class for PASA Research papers"""

from datetime import datetime
from typing import Any
from urllib.parse import urlencode

from rich.console import Console

from ..core.api_client import PasaApiClient
from ..models.config import FetcherConfig
from ..models.paper import Paper
from ..scrapers.arxiv_scraper import ArxivScraper
from ..utils.cache import Cache
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class PasaFetcher:
    """Main class for fetching research papers from pasa-agent.ai"""

    def __init__(self, config: FetcherConfig | None = None):
        self.config = config or FetcherConfig()
        self.cache = Cache(enabled=self.config.cache_enabled, ttl=self.config.cache_ttl)
        self.api_client = PasaApiClient(
            timeout=self.config.timeout // 1000
        )  # Convert ms to seconds
        self.arxiv_scraper = ArxivScraper()

    async def __aenter__(self) -> "PasaFetcher":
        """Async context manager entry"""
        await self.api_client.__aenter__()
        logger.info("PASA API client initialized")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.api_client.__aexit__(exc_type, exc_val, exc_tb)
        logger.info("PASA API client closed")

    def build_pasa_url(self, query: str, session_id: str | None = None) -> str:
        """Build PASA agent URL with query parameters"""
        base_url = "https://pasa-agent.ai/home"
        params = {"query": query}
        if session_id:
            params["session"] = session_id
        else:
            # Generate session ID based on timestamp
            params["session"] = str(int(datetime.now().timestamp() * 1000000))

        return f"{base_url}?{urlencode(params)}"

    async def fetch_papers(self, query: str, max_results: int | None = None) -> list[Paper]:
        """
        Fetch research papers based on query

        Args:
            query: Search query for papers
            max_results: Maximum number of papers to return

        Returns:
            List of Paper objects
        """
        # Check cache first
        cache_key = f"query:{query}:max:{max_results}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached results for query: {query}")
            return cached_result  # type: ignore

        # Use API client to fetch papers
        papers = await self.api_client.search_papers(query, max_results)

        # Optionally enrich with ArXiv metadata
        if papers:
            enriched_papers = []
            for paper in papers:
                enriched_paper = await self._enrich_with_arxiv_data(paper)
                enriched_papers.append(enriched_paper)
            papers = enriched_papers

        # Cache results
        await self.cache.set(cache_key, papers)

        return papers

    async def fetch_papers_until_complete(
        self, query: str, max_results: int | None = None, sort_by_relevance: bool = True
    ) -> list[Paper]:
        """
        Fetch research papers with guarantee that task runs until fully complete.
        This method ensures complete results are returned, sorted by relevance.

        Args:
            query: Search query for papers
            max_results: Maximum number of papers to return
            sort_by_relevance: Whether to sort results by relevance score (highest first)

        Returns:
            List of Paper objects, guaranteed to be complete and sorted
        """
        # Check cache first
        cache_key = f"complete:{query}:max:{max_results}:sorted:{sort_by_relevance}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached complete results for query: {query}")
            return cached_result  # type: ignore

        logger.info(f"Starting guaranteed complete search for: {query}")

        # Use API client with extended polling to ensure complete results
        papers = await self.api_client.search_papers_complete(query, max_results)

        # Enrich with ArXiv metadata
        if papers:
            enriched_papers = []
            for paper in papers:
                enriched_paper = await self._enrich_with_arxiv_data(paper)
                enriched_papers.append(enriched_paper)
            papers = enriched_papers

        # Sort by relevance if requested
        if sort_by_relevance and papers:
            papers.sort(key=lambda p: p.relevance_score or 0.0, reverse=True)
            logger.info(f"Sorted {len(papers)} papers by relevance score")

        # Cache complete results
        await self.cache.set(cache_key, papers)

        logger.info(
            f"Completed search with {len(papers)} papers (scores: {papers[0].relevance_score:.3f}-{papers[-1].relevance_score:.3f})"
            if papers
            else "Completed search with 0 papers"
        )

        return papers

    async def _enrich_with_arxiv_data(self, paper: Paper) -> Paper:
        """Enrich paper with additional ArXiv metadata"""
        try:
            arxiv_details = await self.arxiv_scraper.get_paper_details(paper.metadata.arxiv_id)
            if arxiv_details:
                # Update metadata with ArXiv details
                if arxiv_details.get("categories"):
                    paper.metadata.categories = arxiv_details["categories"]
                if arxiv_details.get("primary_category"):
                    paper.metadata.primary_category = arxiv_details["primary_category"]
                if arxiv_details.get("doi"):
                    paper.metadata.doi = arxiv_details["doi"]
                if arxiv_details.get("journal_ref"):
                    paper.metadata.journal_ref = arxiv_details["journal_ref"]
                if arxiv_details.get("comments"):
                    paper.metadata.comments = arxiv_details["comments"]

                logger.debug(f"Enriched paper {paper.metadata.arxiv_id} with ArXiv data")

            return paper

        except Exception as e:
            logger.warning(f"Could not enrich paper {paper.metadata.arxiv_id}: {e}")
            return paper

    async def download_papers(
        self, papers: list[Paper], output_dir: str = "./downloads"
    ) -> dict[str, dict[str, str]]:
        """
        Download PDF and TeX files for papers

        Args:
            papers: List of Paper objects
            output_dir: Directory to save files

        Returns:
            Dictionary mapping paper IDs to dictionaries of file paths
        """
        from ..utils.downloader import PaperDownloader

        downloader = PaperDownloader(
            max_concurrent=self.config.max_concurrent_downloads, output_dir=output_dir
        )

        return await downloader.download_papers(
            papers, download_pdfs=self.config.download_pdfs, download_tex=self.config.download_tex
        )
