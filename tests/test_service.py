"""Test service functions"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import HttpUrl

from pasa_research_fetcher.models.paper import Author, Paper, PaperMetadata
from pasa_research_fetcher.service import (
    get_paper_metadata,
    get_paper_metadata_sync,
    search_papers,
    search_papers_sync,
)


class TestServiceFunctions:
    """Test high-level service functions"""

    def create_mock_paper(self, arxiv_id="2301.00001", title="Test Paper"):
        """Create a mock paper for testing"""
        metadata = PaperMetadata(
            arxiv_id=arxiv_id,
            title=title,
            authors=[Author(name="Test Author")],
            abstract="Test abstract",
            published_date=datetime(2023, 1, 1),
            categories=["cs.AI"],
        )

        return Paper(
            metadata=metadata,
            pdf_url=HttpUrl(f"https://arxiv.org/pdf/{arxiv_id}.pdf"),
            arxiv_url=HttpUrl(f"https://arxiv.org/abs/{arxiv_id}"),
            relevance_score=0.9,
        )

    @pytest.mark.asyncio
    async def test_search_papers_async(self):
        """Test async search_papers function"""
        mock_paper = self.create_mock_paper()

        with patch("pasa_research_fetcher.service.PasaFetcher") as mock_fetcher_class:
            # Setup mock
            mock_fetcher = AsyncMock()
            mock_fetcher.fetch_papers.return_value = [mock_paper]
            mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

            # Test function
            papers = await search_papers("test query", max_results=5)

            # Verify results
            assert len(papers) == 1
            assert papers[0].metadata.title == "Test Paper"
            assert papers[0].metadata.arxiv_id == "2301.00001"

            # Verify fetcher was called correctly
            mock_fetcher.fetch_papers.assert_called_once_with("test query", 5)

    def test_search_papers_sync(self):
        """Test sync search_papers_sync function"""
        mock_paper = self.create_mock_paper()

        with patch("pasa_research_fetcher.service.PasaFetcher") as mock_fetcher_class:
            # Setup mock
            mock_fetcher = AsyncMock()
            mock_fetcher.fetch_papers.return_value = [mock_paper]
            mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

            # Test function
            papers = search_papers_sync("test query", max_results=3)

            # Verify results
            assert len(papers) == 1
            assert papers[0].metadata.title == "Test Paper"

    @pytest.mark.asyncio
    async def test_get_paper_metadata(self):
        """Test get_paper_metadata function"""
        mock_paper = self.create_mock_paper(arxiv_id="2301.00002", title="Another Test Paper")

        with patch("pasa_research_fetcher.service.search_papers") as mock_search:
            mock_search.return_value = [mock_paper]

            # Test function
            metadata = await get_paper_metadata("test query", max_results=1)

            # Verify results
            assert len(metadata) == 1
            assert metadata[0]["arxiv_id"] == "2301.00002"
            assert metadata[0]["title"] == "Another Test Paper"
            assert metadata[0]["authors"] == ["Test Author"]
            assert metadata[0]["relevance_score"] == 0.9
            assert "pdf_url" in metadata[0]
            assert "arxiv_url" in metadata[0]

    def test_get_paper_metadata_sync(self):
        """Test sync get_paper_metadata_sync function"""
        mock_paper = self.create_mock_paper()

        with patch("pasa_research_fetcher.service.search_papers") as mock_search:
            mock_search.return_value = [mock_paper]

            # Test function
            metadata = get_paper_metadata_sync("test query")

            # Verify results
            assert len(metadata) == 1
            assert metadata[0]["title"] == "Test Paper"
            assert isinstance(metadata[0], dict)

    @pytest.mark.asyncio
    async def test_search_papers_empty_result(self):
        """Test search_papers with empty results"""
        with patch("pasa_research_fetcher.service.PasaFetcher") as mock_fetcher_class:
            # Setup mock to return empty list
            mock_fetcher = AsyncMock()
            mock_fetcher.fetch_papers.return_value = []
            mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

            # Test function
            papers = await search_papers("nonexistent query")

            # Verify empty result
            assert len(papers) == 0
            assert isinstance(papers, list)

    @pytest.mark.asyncio
    async def test_get_paper_metadata_date_serialization(self):
        """Test metadata serialization handles dates correctly"""
        # Create paper with None published_date
        metadata = PaperMetadata(
            arxiv_id="2301.00003",
            title="No Date Paper",
            abstract="Test abstract",
            published_date=None,  # Test None date handling
        )

        paper = Paper(
            metadata=metadata,
            pdf_url=HttpUrl("https://arxiv.org/pdf/2301.00003.pdf"),
            arxiv_url=HttpUrl("https://arxiv.org/abs/2301.00003"),
        )

        with patch("pasa_research_fetcher.service.search_papers") as mock_search:
            mock_search.return_value = [paper]

            # Test function
            metadata_result = await get_paper_metadata("test query")

            # Verify None date is handled
            assert metadata_result[0]["published_date"] is None
