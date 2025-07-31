#!/usr/bin/env python3
"""Basic usage examples for PASA Research Fetcher"""

import asyncio
from pasa_research_fetcher import (
    search_papers,
    search_papers_sync,
    search_and_download,
    get_paper_metadata_sync
)


def example_sync_search():
    """Example of synchronous paper search"""
    print("=== Synchronous Search Example ===")
    
    query = "transformer neural networks"
    papers = search_papers_sync(query)
    
    print(f"Found {len(papers)} papers for query: '{query}'")
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.metadata.title}")
        print(f"   Authors: {', '.join([a.name for a in paper.metadata.authors])}")
        print(f"   ArXiv ID: {paper.metadata.arxiv_id}")
        print(f"   Published: {paper.metadata.published_date}")
        print(f"   Relevance Score: {paper.relevance_score:.3f}")
        print(f"   PDF: {paper.pdf_url}")


async def example_async_search():
    """Example of asynchronous paper search"""
    print("\n=== Asynchronous Search Example ===")
    
    query = "attention mechanism"
    papers = await search_papers(query)
    
    print(f"Found {len(papers)} papers for query: '{query}'")
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.metadata.title}")
        print(f"   Abstract: {paper.metadata.abstract[:200]}...")


async def example_search_and_download():
    """Example of searching and downloading papers"""
    print("\n=== Search and Download Example ===")
    
    query = "deep learning"
    result = await search_and_download(
        query,
        output_dir="./example_downloads",
        max_results=2,
        download_pdfs=True,
        download_tex=False
    )
    
    papers = result["papers"]
    downloads = result["downloads"]
    
    print(f"Found {len(papers)} papers for query: '{query}'")
    print(f"Download results:")
    
    for arxiv_id, files in downloads.items():
        print(f"  {arxiv_id}: {files}")


def example_metadata_only():
    """Example of getting just metadata as dictionaries"""
    print("\n=== Metadata Only Example ===")
    
    query = "machine learning"
    metadata = get_paper_metadata_sync(query, max_results=2)
    
    print(f"Got metadata for {len(metadata)} papers:")
    
    import json
    for item in metadata:
        print(f"\nTitle: {item['title']}")
        print(f"Authors: {', '.join(item['authors'])}")
        print(f"ArXiv ID: {item['arxiv_id']}")
        print(f"PDF URL: {item['pdf_url']}")


def example_custom_config():
    """Example using custom configuration"""
    print("\n=== Custom Configuration Example ===")
    
    from pasa_research_fetcher import FetcherConfig
    
    # Create custom config
    config = FetcherConfig(
        timeout=45000,  # 45 seconds
        cache_enabled=True,
        cache_ttl=7200,  # 2 hours
        download_pdfs=True,
        download_tex=True
    )
    
    query = "neural networks"
    papers = search_papers_sync(query, max_results=1, config=config)
    
    print(f"Used custom config to find {len(papers)} papers")
    if papers:
        paper = papers[0]
        print(f"Paper: {paper.metadata.title}")
        print(f"Config used - Timeout: {config.timeout}ms, Cache TTL: {config.cache_ttl}s")


async def main():
    """Run all examples"""
    print("PASA Research Fetcher - Usage Examples")
    print("=====================================")
    
    # Synchronous examples
    example_sync_search()
    example_metadata_only()
    example_custom_config()
    
    # Asynchronous examples
    await example_async_search()
    await example_search_and_download()
    
    print("\n✓ All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())