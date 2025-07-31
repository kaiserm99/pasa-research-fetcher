"""Models for representing research papers"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Author(BaseModel):
    """Author information"""

    name: str
    affiliation: str | None = None
    email: str | None = None


class PaperMetadata(BaseModel):
    """Metadata for a research paper"""

    arxiv_id: str = Field(..., description="ArXiv paper ID")
    title: str = Field(..., description="Paper title")
    authors: list[Author] = Field(default_factory=list, description="List of authors")
    abstract: str = Field(..., description="Paper abstract")
    published_date: datetime | None = Field(default=None, description="Publication date")
    updated_date: datetime | None = Field(default=None, description="Last update date")
    categories: list[str] = Field(default_factory=list, description="ArXiv categories")
    doi: str | None = Field(default=None, description="Digital Object Identifier")
    journal_ref: str | None = Field(default=None, description="Journal reference")
    comments: str | None = Field(default=None, description="Additional comments")
    primary_category: str | None = Field(default=None, description="Primary ArXiv category")


class Paper(BaseModel):
    """Complete paper information including links and metadata"""

    metadata: PaperMetadata
    pdf_url: HttpUrl = Field(..., description="URL to PDF file")
    arxiv_url: HttpUrl = Field(..., description="ArXiv paper page URL")
    tex_url: HttpUrl | None = Field(None, description="URL to TeX source if available")
    relevance_score: float | None = Field(None, description="Relevance score from PASA")
    summary: str | None = Field(None, description="PASA-generated summary")
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Extraction timestamp"
    )
    additional_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional extracted data"
    )

    model_config = {
        "json_encoders": {datetime: lambda v: v.isoformat(), HttpUrl: str}
    }
