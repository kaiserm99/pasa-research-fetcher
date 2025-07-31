#!/usr/bin/env python3
"""Example of integrating PASA Research Fetcher into another service"""

import asyncio
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from pasa_research_fetcher import search_papers, PaperMetadata


@dataclass
class ResearchService:
    """Example service that uses PASA Research Fetcher"""

    def __init__(self):
        self.cache = {}
        self.search_history = []

    async def get_papers_for_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get papers for a specific research topic

        This is how you would integrate PASA into your own service
        """
        # Log the search
        self.search_history.append(
            {"topic": topic, "timestamp": datetime.now().isoformat(), "limit": limit}
        )

        # Check cache first
        cache_key = f"{topic}:{limit}"
        if cache_key in self.cache:
            print(f"Returning cached results for: {topic}")
            return self.cache[cache_key]

        # Fetch papers using PASA
        print(f"Fetching papers for topic: {topic}")
        papers = await search_papers(topic, max_results=limit)

        # Process and format the results for your service
        formatted_papers = []
        for paper in papers:
            formatted_paper = {
                "id": paper.metadata.arxiv_id,
                "title": paper.metadata.title,
                "authors": [author.name for author in paper.metadata.authors],
                "abstract": paper.metadata.abstract,
                "published_date": paper.metadata.published_date.isoformat()
                if paper.metadata.published_date
                else None,
                "pdf_url": str(paper.pdf_url),
                "arxiv_url": str(paper.arxiv_url),
                "relevance_score": paper.relevance_score,
                "categories": paper.metadata.categories,
                # Add your own custom fields
                "fetched_at": datetime.now().isoformat(),
                "source": "pasa-agent.ai",
            }
            formatted_papers.append(formatted_paper)

        # Cache the results
        self.cache[cache_key] = formatted_papers

        return formatted_papers

    async def get_papers_by_author(self, author_name: str) -> List[Dict[str, Any]]:
        """Find papers by a specific author"""
        query = f"author:{author_name}"
        return await self.get_papers_for_topic(query)

    async def get_recent_papers(self, topic: str, since_year: int = 2023) -> List[Dict[str, Any]]:
        """Get recent papers on a topic"""
        query = f"{topic} since:{since_year}"
        return await self.get_papers_for_topic(query)

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about searches performed"""
        return {
            "total_searches": len(self.search_history),
            "cached_results": len(self.cache),
            "recent_searches": self.search_history[-5:] if self.search_history else [],
        }

    async def bulk_fetch_papers(
        self, topics: List[str], limit_per_topic: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch papers for multiple topics concurrently"""
        print(f"Bulk fetching papers for {len(topics)} topics...")

        # Create concurrent tasks
        tasks = [self.get_papers_for_topic(topic, limit_per_topic) for topic in topics]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)

        # Combine results
        return dict(zip(topics, results))


async def example_service_integration():
    """Example of how to integrate PASA into your service"""
    print("=== Service Integration Example ===")

    # Create your service instance
    service = ResearchService()

    # Example 1: Get papers for a research topic
    papers = await service.get_papers_for_topic("machine learning", limit=3)
    print(f"Found {len(papers)} papers on machine learning")

    # Example 2: Get papers by author (if supported by PASA)
    # papers = await service.get_papers_by_author("Geoffrey Hinton")

    # Example 3: Get recent papers
    papers = await service.get_recent_papers("transformer", since_year=2023)
    print(f"Found {len(papers)} recent papers on transformers")

    # Example 4: Bulk fetch for multiple topics
    topics = ["neural networks", "computer vision"]
    bulk_results = await service.bulk_fetch_papers(topics, limit_per_topic=2)

    print(f"Bulk fetch results:")
    for topic, papers in bulk_results.items():
        print(f"  {topic}: {len(papers)} papers")

    # Example 5: Get service statistics
    stats = service.get_search_statistics()
    print(f"Service statistics: {json.dumps(stats, indent=2)}")


class PaperDatabase:
    """Example of storing PASA results in a database-like structure"""

    def __init__(self):
        self.papers = {}  # In real app, this would be a database

    async def fetch_and_store(self, query: str, max_results: int = 20):
        """Fetch papers and store them"""
        print(f"Fetching and storing papers for: {query}")

        papers = await search_papers(query, max_results=max_results)

        for paper in papers:
            # Store in our "database"
            self.papers[paper.metadata.arxiv_id] = {
                "title": paper.metadata.title,
                "authors": [a.name for a in paper.metadata.authors],
                "abstract": paper.metadata.abstract,
                "published_date": paper.metadata.published_date,
                "pdf_url": str(paper.pdf_url),
                "arxiv_url": str(paper.arxiv_url),
                "relevance_score": paper.relevance_score,
                "query_used": query,
                "stored_at": datetime.now(),
            }

        print(f"Stored {len(papers)} papers in database")

    def search_stored_papers(self, keyword: str) -> List[Dict[str, Any]]:
        """Search through stored papers"""
        results = []
        for arxiv_id, paper in self.papers.items():
            if (
                keyword.lower() in paper["title"].lower()
                or keyword.lower() in paper["abstract"].lower()
            ):
                results.append({**paper, "arxiv_id": arxiv_id})
        return results

    def get_papers_by_year(self, year: int) -> List[Dict[str, Any]]:
        """Get papers published in a specific year"""
        results = []
        for arxiv_id, paper in self.papers.items():
            if paper["published_date"] and paper["published_date"].year == year:
                results.append({**paper, "arxiv_id": arxiv_id})
        return results


async def example_database_integration():
    """Example of integrating with a database"""
    print("\n=== Database Integration Example ===")

    db = PaperDatabase()

    # Fetch and store papers for different topics
    await db.fetch_and_store("deep learning", max_results=5)
    await db.fetch_and_store("natural language processing", max_results=5)

    print(f"Total papers in database: {len(db.papers)}")

    # Search stored papers
    results = db.search_stored_papers("attention")
    print(f"Found {len(results)} papers mentioning 'attention'")

    # Get papers by year
    results_2024 = db.get_papers_by_year(2024)
    print(f"Found {len(results_2024)} papers from 2024")


async def main():
    """Run integration examples"""
    print("PASA Research Fetcher - Integration Examples")
    print("==========================================")

    await example_service_integration()
    await example_database_integration()

    print("\n✓ All integration examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
