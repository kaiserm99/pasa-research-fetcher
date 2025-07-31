"""PASA Research Fetcher - Extract research papers from pasa-agent.ai"""

__version__ = "0.1.0"
__author__ = "Marco Kaiser"
__email__ = "marco99kaiser@googlemail.com"

from .core.fetcher import PasaFetcher
from .models.config import FetcherConfig
from .models.paper import Author, Paper, PaperMetadata
from .service import (
    get_paper_metadata,
    get_paper_metadata_sync,
    search_and_download,
    search_and_download_sync,
    search_papers,
    search_papers_complete,
    search_papers_complete_sync,
    search_papers_sync,
)

__all__ = [
    "PasaFetcher",
    "Paper",
    "PaperMetadata",
    "Author",
    "FetcherConfig",
    "search_papers",
    "search_papers_complete",
    "search_and_download",
    "search_papers_sync",
    "search_papers_complete_sync",
    "search_and_download_sync",
    "get_paper_metadata",
    "get_paper_metadata_sync",
]
