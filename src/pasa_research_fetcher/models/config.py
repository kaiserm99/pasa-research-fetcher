"""Configuration models for PASA Research Fetcher"""

from pydantic import BaseModel, Field


class FetcherConfig(BaseModel):
    """Configuration for PasaFetcher"""

    headless: bool = Field(default=True, description="Run browser in headless mode")
    timeout: int = Field(default=60000, description="Request timeout in milliseconds")
    wait_for_selector: str = Field(
        default="All Papers Found", description="Text to wait for indicating page load complete"
    )
    max_concurrent_downloads: int = Field(default=5, description="Maximum concurrent PDF downloads")
    download_pdfs: bool = Field(default=True, description="Whether to download PDF files")
    download_tex: bool = Field(default=False, description="Whether to download TeX source files")
    cache_enabled: bool = Field(default=True, description="Enable caching of fetched data")
    cache_ttl: int = Field(default=3600, description="Cache time-to-live in seconds")
    user_agent: str | None = Field(default=None, description="Custom user agent string")
    proxy: str | None = Field(default=None, description="Proxy URL for requests")
