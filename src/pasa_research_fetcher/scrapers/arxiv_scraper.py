"""Scraper for arxiv.org to get additional paper details"""

import re
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ArxivScraper:
    """Scraper for extracting additional information from ArXiv"""

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_paper_details(self, arxiv_id: str) -> dict[str, Any] | None:
        """
        Get detailed paper information from ArXiv

        Args:
            arxiv_id: ArXiv paper ID (e.g., "2301.00001")

        Returns:
            Dictionary with paper details or None
        """
        try:
            url = f"https://arxiv.org/abs/{arxiv_id}"
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            details = {}

            # Extract title
            title_elem = soup.find("h1", class_="title")
            if title_elem:
                details["title"] = title_elem.text.replace("Title:", "").strip()

            # Extract authors with affiliations
            authors_elem = soup.find("div", class_="authors")
            if authors_elem:
                details["authors"] = self._extract_authors(authors_elem)

            # Extract abstract
            abstract_elem = soup.find("blockquote", class_="abstract")
            if abstract_elem:
                details["abstract"] = abstract_elem.text.replace("Abstract:", "").strip()

            # Extract dates
            dateline = soup.find("div", class_="dateline")
            if dateline:
                dates = self._extract_dates(dateline.text)
                details.update(dates)

            # Extract categories
            subjects_elem = soup.find("span", class_="primary-subject")
            if subjects_elem:
                details["primary_category"] = subjects_elem.text.strip()

            all_subjects = soup.find_all("span", class_="primary-subject") + soup.find_all(
                "a", {"class": "taxon"}
            )
            details["categories"] = list({elem.text.strip() for elem in all_subjects})

            # Extract DOI
            doi_elem = soup.find("a", href=re.compile(r"doi\.org"))
            if doi_elem and hasattr(doi_elem, "get"):
                href = doi_elem.get("href")
                if href:
                    details["doi"] = href.split("doi.org/")[-1]

            # Extract journal reference
            journal_ref = soup.find("td", class_="tablecell", string="Journal ref:")
            if journal_ref and journal_ref.next_sibling:
                details["journal_ref"] = journal_ref.next_sibling.text.strip()

            # Extract comments
            comments = soup.find("td", class_="tablecell", string="Comments:")
            if comments and comments.next_sibling:
                details["comments"] = comments.next_sibling.text.strip()

            # Check if TeX source is available
            tex_link = soup.find("a", href=re.compile(r"/e-print/"))
            details["has_tex_source"] = tex_link is not None

            return details

        except Exception as e:
            logger.error(f"Error fetching ArXiv details for {arxiv_id}: {e}")
            return None

    def _extract_authors(self, authors_elem: Any) -> list[dict[str, str]]:
        """Extract authors with their affiliations"""
        authors = []
        author_links = authors_elem.find_all("a")

        for link in author_links:
            author = {"name": link.text.strip()}
            # Try to find affiliation (usually in parentheses after name)
            next_text = link.next_sibling
            if next_text and isinstance(next_text, str):
                affil_match = re.search(r"\((.*?)\)", next_text)
                if affil_match:
                    author["affiliation"] = affil_match.group(1)
            authors.append(author)

        return authors

    def _extract_dates(self, dateline_text: str) -> dict[str, datetime]:
        """Extract submission and update dates from dateline"""
        dates = {}

        # Extract submission date
        submitted_match = re.search(r"Submitted on (\d+ \w+ \d{4})", dateline_text)
        if submitted_match:
            try:
                dates["published_date"] = datetime.strptime(submitted_match.group(1), "%d %b %Y")
            except ValueError:
                pass

        # Extract last update date
        updated_match = re.search(r"last revised (\d+ \w+ \d{4})", dateline_text)
        if updated_match:
            try:
                dates["updated_date"] = datetime.strptime(updated_match.group(1), "%d %b %Y")
            except ValueError:
                pass

        return dates

    async def close(self) -> None:
        """Close HTTP client"""
        await self.client.aclose()
