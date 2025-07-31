"""Test API client functionality"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from pasa_research_fetcher.core.api_client import PasaApiClient


class TestPasaApiClient:
    """Test PASA API client"""

    @pytest.fixture
    def api_client(self):
        """Create API client for testing"""
        return PasaApiClient(timeout=30, max_retries=2)

    @pytest.fixture
    def mock_response_data(self):
        """Mock API response data"""
        return {
            "base_resp": {"status_code": 0},
            "papers": json.dumps({
                "paper_1": {
                    "entry_id": "2301.00001",
                    "title": "Test Paper Title",
                    "authors": ["John Doe", "Jane Smith"],
                    "abstract": "This is a test abstract for the paper.",
                    "publish_time": "20230101",
                    "score": 0.95,
                    "source": "arxiv",
                    "select_reason": "high relevance",
                    "bib_result": "@article{test2023}",
                    "json_result": "{}"
                }
            }),
            "finish": True
        }

    def test_generate_session_id(self, api_client):
        """Test session ID generation"""
        session_id = api_client._generate_session_id()
        
        assert isinstance(session_id, str)
        assert len(session_id) > 10  # Should be timestamp-based
        assert session_id.isdigit()

    @pytest.mark.asyncio
    async def test_initiate_search_success(self, api_client, mock_response_data):
        """Test successful search initiation"""
        with patch.object(api_client.client, 'post') as mock_post:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data  # Not async
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Test initiation
            await api_client._initiate_search("test query", "12345")
            
            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "single_paper_agent" in call_args[0][0]
            assert call_args[1]["json"]["user_query"] == "test query"
            assert call_args[1]["json"]["session_id"] == "12345"

    @pytest.mark.asyncio
    async def test_initiate_search_retry_on_failure(self, api_client):
        """Test search initiation retries on failure"""
        with patch.object(api_client.client, 'post') as mock_post:
            # Setup mock to fail then succeed
            success_response = MagicMock()
            success_response.json.return_value = {"base_resp": {"status_code": 0}}
            success_response.raise_for_status.return_value = None
            
            mock_post.side_effect = [
                Exception("Network error"),
                success_response
            ]
            
            # Test initiation (should succeed after retry)
            await api_client._initiate_search("test query", "12345")
            
            # Verify retry happened
            assert mock_post.call_count == 2

    @pytest.mark.asyncio
    async def test_poll_results_immediate_success(self, api_client, mock_response_data):
        """Test polling when results are immediately available"""
        with patch.object(api_client.client, 'post') as mock_post:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Test polling
            result = await api_client._poll_results("12345", poll_interval=0.1, max_polls=5)
            
            # Verify result
            assert len(result) == 1
            assert "paper_1" in result
            assert result["paper_1"]["title"] == "Test Paper Title"

    @pytest.mark.asyncio
    async def test_poll_results_gradual_loading(self, api_client):
        """Test polling with gradual paper loading"""
        with patch.object(api_client.client, 'post') as mock_post:
            # Setup progressive responses - final response should trigger completion
            stable_response = {"base_resp": {"status_code": 0}, "papers": json.dumps({"paper_1": {"entry_id": "2301.00001", "title": "Paper 1", "authors": [], "abstract": "Abstract 1", "publish_time": "", "score": 0.8}}), "finish": True}
            
            responses = [
                # First poll - no papers
                {"base_resp": {"status_code": 0}, "papers": "{}", "finish": False},
                # Second poll - one paper appears
                {"base_resp": {"status_code": 0}, "papers": json.dumps({"paper_1": {"entry_id": "2301.00001", "title": "Paper 1", "authors": [], "abstract": "Abstract 1", "publish_time": "", "score": 0.8}}), "finish": False},
                # Third poll - stable count
                stable_response,
                # Fourth and subsequent polls - same stable response
                stable_response,
                stable_response,
            ]
            
            # Create properly configured mock responses
            mock_responses = []
            for resp in responses:
                mock_resp = MagicMock()
                mock_resp.json.return_value = resp
                mock_resp.raise_for_status.return_value = None
                mock_responses.append(mock_resp)
            
            mock_post.side_effect = mock_responses
            
            # Test polling with fewer max polls to avoid running out of responses
            result = await api_client._poll_results("12345", poll_interval=0.1, max_polls=5)
            
            # Verify result
            assert len(result) == 1
            assert "paper_1" in result

    def test_parse_papers(self, api_client):
        """Test paper parsing from API data"""
        papers_data = {
            "paper_1": {
                "entry_id": "2301.00001",
                "title": "Machine Learning Paper",
                "authors": ["Alice Johnson", "Bob Wilson"],
                "abstract": "A comprehensive study of ML techniques.",
                "publish_time": "20230115",
                "score": 0.92,
                "source": "arxiv",
                "select_reason": "highly relevant to query",
                "bib_result": "@article{johnson2023ml}",
                "json_result": "{\"category\": \"cs.LG\"}"
            }
        }
        
        papers = api_client._parse_papers(papers_data, "machine learning")
        
        assert len(papers) == 1
        paper = papers[0]
        assert paper.metadata.arxiv_id == "2301.00001"
        assert paper.metadata.title == "Machine Learning Paper"
        assert len(paper.metadata.authors) == 2
        assert paper.metadata.authors[0].name == "Alice Johnson"
        assert paper.relevance_score == 0.92
        assert paper.additional_data["user_query"] == "machine learning"

    def test_create_paper_from_api_data_date_parsing(self, api_client):
        """Test date parsing in paper creation"""
        paper_info = {
            "entry_id": "2301.00001",
            "title": "Test Paper",
            "authors": ["Test Author"],
            "abstract": "Test abstract",
            "publish_time": "20230325",  # March 25, 2023
            "score": 0.85,
            "source": "arxiv"
        }
        
        paper = api_client._create_paper_from_api_data(paper_info, "test query")
        
        assert paper is not None
        assert paper.metadata.published_date is not None
        assert paper.metadata.published_date.year == 2023
        assert paper.metadata.published_date.month == 3
        assert paper.metadata.published_date.day == 25

    def test_create_paper_from_api_data_invalid_date(self, api_client):
        """Test handling of invalid date formats"""
        paper_info = {
            "entry_id": "2301.00001",
            "title": "Test Paper",
            "authors": ["Test Author"],
            "abstract": "Test abstract",
            "publish_time": "invalid_date",
            "score": 0.85,
            "source": "arxiv"
        }
        
        paper = api_client._create_paper_from_api_data(paper_info, "test query")
        
        assert paper is not None
        assert paper.metadata.published_date is None  # Should handle invalid date gracefully

    def test_create_paper_from_api_data_missing_fields(self, api_client):
        """Test paper creation with missing optional fields"""
        paper_info = {
            "entry_id": "2301.00001",
            "title": "Minimal Paper",
            # Missing authors, abstract, etc.
        }
        
        paper = api_client._create_paper_from_api_data(paper_info, "test query")
        
        assert paper is not None
        assert paper.metadata.arxiv_id == "2301.00001"
        assert paper.metadata.title == "Minimal Paper"
        assert len(paper.metadata.authors) == 0
        assert paper.metadata.abstract == ""