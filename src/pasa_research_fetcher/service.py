"""High-level service functions for easy integration"""

import asyncio
from typing import Any

from .core.fetcher import PasaFetcher
from .models.config import FetcherConfig
from .models.paper import Paper


async def search_papers(
    query: str, max_results: int | None = None, config: FetcherConfig | None = None
) -> list[Paper]:
    """
    Search for research papers using PASA agent

    Args:
        query: Search query for papers
        max_results: Maximum number of results to return
        config: Optional configuration object

    Returns:
        List of Paper objects

    Example:
        ```python
        import asyncio
        from pasa_research_fetcher import search_papers

        async def main():
            papers = await search_papers("attention mechanism", max_results=5)
            for paper in papers:
                print(f"{paper.metadata.title} - {paper.pdf_url}")

        asyncio.run(main())
        ```
    """
    async with PasaFetcher(config) as fetcher:
        return await fetcher.fetch_papers(query, max_results)


async def search_papers_complete(
    query: str,
    max_results: int | None = None,
    sort_by_relevance: bool = True,
    config: FetcherConfig | None = None,
) -> list[Paper]:
    """
    Search for research papers with completion guarantee and relevance sorting.

    This function ensures the search runs until fully complete, returning all
    available papers sorted by relevance score (highest first by default).

    Args:
        query: Search query for papers
        max_results: Maximum number of results to return
        sort_by_relevance: Whether to sort results by relevance score (highest first)
        config: Optional configuration object

    Returns:
        List of Paper objects, guaranteed to be complete and sorted

    Example:
        ```python
        import asyncio
        from pasa_research_fetcher import search_papers_complete

        async def main():
            # Get complete results sorted by relevance
            papers = await search_papers_complete(
                "machine learning transformers",
                max_results=20,
                sort_by_relevance=True
            )

            print(f"Found {len(papers)} papers")
            for paper in papers[:5]:  # Show top 5
                print(f"{paper.metadata.title}")
                print(f"  Score: {paper.relevance_score:.3f}")
                print(f"  Authors: {[a.name for a in paper.metadata.authors[:2]]}")
                print()

        asyncio.run(main())
        ```
    """
    async with PasaFetcher(config) as fetcher:
        return await fetcher.fetch_papers_until_complete(query, max_results, sort_by_relevance)


async def search_and_download(
    query: str,
    output_dir: str = "./downloads",
    max_results: int | None = None,
    download_pdfs: bool = True,
    download_tex: bool = False,
    config: FetcherConfig | None = None,
) -> dict[str, Any]:
    """
    Search for papers and download them

    Args:
        query: Search query for papers
        output_dir: Directory to save downloaded files
        max_results: Maximum number of results
        download_pdfs: Whether to download PDF files
        download_tex: Whether to download TeX source files
        config: Optional configuration object

    Returns:
        Dictionary with 'papers' and 'downloads' keys

    Example:
        ```python
        result = await search_and_download(
            "transformer neural networks",
            output_dir="./papers",
            max_results=3
        )
        print(f"Found {len(result['papers'])} papers")
        print(f"Download results: {result['downloads']}")
        ```
    """
    if config is None:
        config = FetcherConfig(download_pdfs=download_pdfs, download_tex=download_tex)

    async with PasaFetcher(config) as fetcher:
        papers = await fetcher.fetch_papers(query, max_results)

        if papers and (download_pdfs or download_tex):
            downloads = await fetcher.download_papers(papers, output_dir)
        else:
            downloads = {}

        return {"papers": papers, "downloads": downloads}


def search_papers_sync(
    query: str, max_results: int | None = None, config: FetcherConfig | None = None
) -> list[Paper]:
    """
    Synchronous wrapper for search_papers

    Args:
        query: Search query for papers
        max_results: Maximum number of results to return
        config: Optional configuration object

    Returns:
        List of Paper objects

    Example:
        ```python
        from pasa_research_fetcher import search_papers_sync

        papers = search_papers_sync("deep learning", max_results=10)
        for paper in papers:
            print(f"{paper.metadata.title}")
        ```
    """
    try:
        # Try to get the current event loop
        _ = asyncio.get_running_loop()
        # If we're in an async context, we need to run in a new thread
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, search_papers(query, max_results, config))
            return future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(search_papers(query, max_results, config))


def search_papers_complete_sync(
    query: str,
    max_results: int | None = None,
    sort_by_relevance: bool = True,
    config: FetcherConfig | None = None,
) -> list[Paper]:
    """
    Synchronous wrapper for search_papers_complete with completion guarantee

    This function ensures the search runs until fully complete, returning all
    available papers sorted by relevance score (highest first by default).

    Args:
        query: Search query for papers
        max_results: Maximum number of results to return
        sort_by_relevance: Whether to sort results by relevance score (highest first)
        config: Optional configuration object

    Returns:
        List of Paper objects, guaranteed to be complete and sorted

    Example:
        ```python
        from pasa_research_fetcher import search_papers_complete_sync

        # Get complete results sorted by relevance
        papers = search_papers_complete_sync(
            "neural networks attention mechanism",
            max_results=15,
            sort_by_relevance=True
        )

        print(f"Found {len(papers)} papers")
        for paper in papers[:3]:  # Show top 3
            print(f"{paper.metadata.title}")
            print(f"  Score: {paper.relevance_score:.3f}")
            print(f"  PDF: {paper.pdf_url}")
            print()
        ```
    """
    try:
        # Try to get the current event loop
        _ = asyncio.get_running_loop()
        # If we're in an async context, we need to run in a new thread
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run, search_papers_complete(query, max_results, sort_by_relevance, config)
            )
            return future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(search_papers_complete(query, max_results, sort_by_relevance, config))


def search_and_download_sync(
    query: str,
    output_dir: str = "./downloads",
    max_results: int | None = None,
    download_pdfs: bool = True,
    download_tex: bool = False,
    config: FetcherConfig | None = None,
) -> dict[str, Any]:
    """
    Synchronous wrapper for search_and_download

    Args:
        query: Search query for papers
        output_dir: Directory to save downloaded files
        max_results: Maximum number of results
        download_pdfs: Whether to download PDF files
        download_tex: Whether to download TeX source files
        config: Optional configuration object

    Returns:
        Dictionary with 'papers' and 'downloads' keys
    """
    try:
        # Try to get the current event loop
        _ = asyncio.get_running_loop()
        # If we're in an async context, we need to run in a new thread
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                search_and_download(
                    query, output_dir, max_results, download_pdfs, download_tex, config
                ),
            )
            return future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(
            search_and_download(query, output_dir, max_results, download_pdfs, download_tex, config)
        )


# Convenience function for getting just paper metadata
async def get_paper_metadata(query: str, max_results: int | None = None) -> list[dict[str, Any]]:
    """
    Get paper metadata as simple dictionaries for easy serialization

    Args:
        query: Search query for papers
        max_results: Maximum number of results

    Returns:
        List of paper metadata dictionaries

    Example:
        ```python
        metadata = await get_paper_metadata("machine learning", max_results=5)
        import json
        print(json.dumps(metadata, indent=2, default=str))
        ```
    """
    papers = await search_papers(query, max_results)
    return [
        {
            "arxiv_id": paper.metadata.arxiv_id,
            "title": paper.metadata.title,
            "authors": [author.name for author in paper.metadata.authors],
            "abstract": paper.metadata.abstract,
            "published_date": (
                paper.metadata.published_date.isoformat() if paper.metadata.published_date else None
            ),
            "pdf_url": str(paper.pdf_url),
            "arxiv_url": str(paper.arxiv_url),
            "relevance_score": paper.relevance_score,
            "categories": paper.metadata.categories,
        }
        for paper in papers
    ]


def get_paper_metadata_sync(query: str, max_results: int | None = None) -> list[dict[str, Any]]:
    """Synchronous wrapper for get_paper_metadata"""
    try:
        # Try to get the current event loop
        _ = asyncio.get_running_loop()
        # If we're in an async context, we need to run in a new thread
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, get_paper_metadata(query, max_results))
            return future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(get_paper_metadata(query, max_results))
