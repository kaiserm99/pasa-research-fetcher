"""Test pydantic models"""

import pytest
from datetime import datetime, timezone
from pydantic import HttpUrl

from pasa_research_fetcher.models.paper import Paper, PaperMetadata, Author
from pasa_research_fetcher.models.config import FetcherConfig


class TestAuthor:
    """Test Author model"""

    def test_author_basic(self):
        """Test basic author creation"""
        author = Author(name="John Doe")
        assert author.name == "John Doe"
        assert author.affiliation is None
        assert author.email is None

    def test_author_full(self):
        """Test author with all fields"""
        author = Author(
            name="Jane Smith",
            affiliation="MIT",
            email="jane@mit.edu"
        )
        assert author.name == "Jane Smith"
        assert author.affiliation == "MIT"
        assert author.email == "jane@mit.edu"


class TestPaperMetadata:
    """Test PaperMetadata model"""

    def test_metadata_minimal(self):
        """Test minimal metadata creation"""
        metadata = PaperMetadata(
            arxiv_id="2301.00001",
            title="Test Paper",
            abstract="This is a test abstract"
        )
        assert metadata.arxiv_id == "2301.00001"
        assert metadata.title == "Test Paper"
        assert metadata.abstract == "This is a test abstract"
        assert len(metadata.authors) == 0
        assert len(metadata.categories) == 0

    def test_metadata_full(self):
        """Test full metadata creation"""
        authors = [Author(name="John Doe"), Author(name="Jane Smith")]
        pub_date = datetime(2023, 1, 1)
        
        metadata = PaperMetadata(
            arxiv_id="2301.00001",
            title="Advanced Machine Learning",
            authors=authors,
            abstract="A comprehensive study of ML techniques",
            published_date=pub_date,
            categories=["cs.AI", "cs.LG"],
            doi="10.48550/arXiv.2301.00001",
            primary_category="cs.AI"
        )
        
        assert len(metadata.authors) == 2
        assert metadata.published_date == pub_date
        assert "cs.AI" in metadata.categories
        assert metadata.doi == "10.48550/arXiv.2301.00001"


class TestPaper:
    """Test Paper model"""

    def test_paper_creation(self):
        """Test paper creation with all required fields"""
        metadata = PaperMetadata(
            arxiv_id="2301.00001",
            title="Test Paper",
            abstract="Test abstract"
        )
        
        paper = Paper(
            metadata=metadata,
            pdf_url=HttpUrl("https://arxiv.org/pdf/2301.00001.pdf"),
            arxiv_url=HttpUrl("https://arxiv.org/abs/2301.00001"),
            relevance_score=0.95
        )
        
        assert paper.metadata.title == "Test Paper"
        assert str(paper.pdf_url) == "https://arxiv.org/pdf/2301.00001.pdf"
        assert paper.relevance_score == 0.95
        assert isinstance(paper.extracted_at, datetime)

    def test_paper_serialization(self):
        """Test paper JSON serialization"""
        metadata = PaperMetadata(
            arxiv_id="2301.00001",
            title="Test Paper",
            abstract="Test abstract"
        )
        
        paper = Paper(
            metadata=metadata,
            pdf_url=HttpUrl("https://arxiv.org/pdf/2301.00001.pdf"),
            arxiv_url=HttpUrl("https://arxiv.org/abs/2301.00001")
        )
        
        json_str = paper.model_dump_json()
        assert "2301.00001" in json_str
        assert "Test Paper" in json_str


class TestFetcherConfig:
    """Test FetcherConfig model"""

    def test_config_defaults(self):
        """Test default configuration values"""
        config = FetcherConfig()
        
        assert config.headless is True
        assert config.timeout == 60000
        assert config.max_concurrent_downloads == 5
        assert config.download_pdfs is True
        assert config.download_tex is False
        assert config.cache_enabled is True

    def test_config_custom(self):
        """Test custom configuration"""
        config = FetcherConfig(
            headless=False,
            timeout=30000,
            download_pdfs=False,
            cache_enabled=False
        )
        
        assert config.headless is False
        assert config.timeout == 30000
        assert config.download_pdfs is False
        assert config.cache_enabled is False