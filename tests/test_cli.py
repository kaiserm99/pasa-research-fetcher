"""Test CLI functionality"""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import HttpUrl
from typer.testing import CliRunner

from pasa_research_fetcher.cli import app
from pasa_research_fetcher.models.paper import Author, Paper, PaperMetadata


class TestCLI:
    """Test CLI commands"""

    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()

    @pytest.fixture
    def mock_paper(self):
        """Create mock paper for testing"""
        metadata = PaperMetadata(
            arxiv_id="2301.00001",
            title="Test CLI Paper",
            authors=[Author(name="CLI Author")],
            abstract="Test abstract for CLI",
            categories=["cs.AI"],
        )

        return Paper(
            metadata=metadata,
            pdf_url=HttpUrl("https://arxiv.org/pdf/2301.00001.pdf"),
            arxiv_url=HttpUrl("https://arxiv.org/abs/2301.00001"),
            relevance_score=0.9,
        )

    def test_cli_help(self, runner):
        """Test CLI help command"""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "PASA Research Fetcher" in result.stdout
        assert "search" in result.stdout
        assert "config" in result.stdout
        assert "version" in result.stdout

    def test_search_command_help(self, runner):
        """Test search command help"""
        result = runner.invoke(app, ["search", "--help"])

        assert result.exit_code == 0
        assert "Search for research papers" in result.stdout
        assert "--max" in result.stdout
        assert "--output" in result.stdout
        assert "--format" in result.stdout

    @patch("pasa_research_fetcher.cli.PasaFetcher")
    def test_search_command_basic(self, mock_fetcher_class, runner, mock_paper):
        """Test basic search command"""
        # Setup mock
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch_papers.return_value = [mock_paper]
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

        # Run command
        result = runner.invoke(app, ["search", "test query", "--no-pdfs"])

        # Verify execution
        assert result.exit_code == 0
        assert "Searching for:" in result.stdout
        assert "Found 1 papers" in result.stdout

        # Verify fetcher was called
        mock_fetcher.fetch_papers.assert_called_once()

    @patch("pasa_research_fetcher.cli.PasaFetcher")
    def test_search_command_with_max_results(self, mock_fetcher_class, runner, mock_paper):
        """Test search command with max results limit"""
        # Setup mock
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch_papers.return_value = [mock_paper]
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

        # Run command with max results
        result = runner.invoke(app, ["search", "test query", "--max", "5", "--no-pdfs"])

        # Verify execution
        assert result.exit_code == 0

        # Verify max_results was passed correctly
        call_args = mock_fetcher.fetch_papers.call_args
        assert call_args[0][1] == 5  # max_results parameter

    @patch("pasa_research_fetcher.cli.PasaFetcher")
    def test_search_command_table_format(self, mock_fetcher_class, runner, mock_paper):
        """Test search command with table output format"""
        # Setup mock
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch_papers.return_value = [mock_paper]
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

        # Run command with table format
        result = runner.invoke(app, ["search", "ml papers", "--format", "table", "--no-pdfs"])

        # Verify execution
        assert result.exit_code == 0
        assert "Research Papers" in result.stdout or "Test CLI Paper" in result.stdout

    @patch("pasa_research_fetcher.cli.PasaFetcher")
    def test_search_command_with_downloads(self, mock_fetcher_class, runner, mock_paper):
        """Test search command with download functionality"""
        # Setup mock
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch_papers.return_value = [mock_paper]
        mock_fetcher.download_papers.return_value = {
            "2301.00001": {"pdf": "/path/to/paper.pdf", "metadata": "/path/to/metadata.json"}
        }
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

        # Run command with downloads enabled
        result = runner.invoke(
            app, ["search", "test query", "--pdfs", "--output", "./test_downloads"]
        )

        # Verify execution
        assert result.exit_code == 0
        assert "Downloading papers" in result.stdout
        assert "Successfully downloaded" in result.stdout

        # Verify download was called
        mock_fetcher.download_papers.assert_called_once()

    @patch("pasa_research_fetcher.cli.PasaFetcher")
    def test_search_command_no_results(self, mock_fetcher_class, runner):
        """Test search command when no papers are found"""
        # Setup mock to return empty results
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch_papers.return_value = []
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

        # Run command
        result = runner.invoke(app, ["search", "nonexistent query", "--no-pdfs"])

        # Verify execution
        assert result.exit_code == 0
        assert "No papers found" in result.stdout

    def test_config_command(self, runner):
        """Test config command"""
        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        # Should output JSON configuration
        assert "{" in result.stdout and "}" in result.stdout
        assert "headless" in result.stdout
        assert "timeout" in result.stdout

    def test_version_command(self, runner):
        """Test version command"""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "PASA Research Fetcher" in result.stdout
        assert "0.1.0" in result.stdout

    @patch("pasa_research_fetcher.cli.PasaFetcher")
    def test_search_command_custom_timeout(self, mock_fetcher_class, runner, mock_paper):
        """Test search command with custom timeout"""
        # Setup mock
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch_papers.return_value = [mock_paper]
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

        # Run command with custom timeout
        result = runner.invoke(app, ["search", "test query", "--timeout", "45000", "--no-pdfs"])

        # Verify execution
        assert result.exit_code == 0

        # Verify config was created with custom timeout
        call_args = mock_fetcher_class.call_args
        config = call_args[0][0] if call_args[0] else None
        if config:
            assert config.timeout == 45000

    @patch("pasa_research_fetcher.cli.PasaFetcher")
    def test_search_command_json_output_format(self, mock_fetcher_class, runner, mock_paper):
        """Test search command with JSON output format"""
        # Setup mock
        mock_fetcher = AsyncMock()
        mock_fetcher.fetch_papers.return_value = [mock_paper]
        mock_fetcher_class.return_value.__aenter__.return_value = mock_fetcher

        # Run command with JSON format (default)
        result = runner.invoke(app, ["search", "test query", "--format", "json", "--no-pdfs"])

        # Verify execution
        assert result.exit_code == 0
        # Should contain JSON-like output with paper data
        assert "Test CLI Paper" in result.stdout or "2301.00001" in result.stdout
