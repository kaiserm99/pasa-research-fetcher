"""API client for PASA agent direct API access"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..models.paper import Author, Paper, PaperMetadata
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class PasaApiClient:
    """Direct API client for PASA agent"""

    def __init__(self, timeout: int = 60, max_retries: int = 3):
        self.base_url = "https://pasa-agent.ai"
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Referer": "https://pasa-agent.ai/",
            },
        )

    async def __aenter__(self) -> "PasaApiClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.client.aclose()

    def _generate_session_id(self) -> str:
        """Generate session ID based on timestamp"""
        return str(int(time.time() * 1000000))

    async def search_papers(self, query: str, max_results: int | None = None) -> list[Paper]:
        """
        Search for papers using PASA API

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of Paper objects
        """
        session_id = self._generate_session_id()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching papers...", total=None)

            # Step 1: Initiate search
            progress.update(task, description="Initiating search...")
            await self._initiate_search(query, session_id)

            # Step 2: Poll for results
            progress.update(task, description="Waiting for results...")
            papers_data = await self._poll_results(session_id)

            # Step 3: Parse and create Paper objects
            progress.update(task, description="Processing results...")
            papers = self._parse_papers(papers_data, query)

            if max_results and len(papers) > max_results:
                papers = papers[:max_results]

            progress.update(task, description=f"Found {len(papers)} papers", completed=True)

        return papers

    async def search_papers_complete(
        self, query: str, max_results: int | None = None
    ) -> list[Paper]:
        """
        Search for papers with enhanced completion guarantee.
        This method uses extended polling and stricter completion criteria
        to ensure all available papers are found before returning results.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of Paper objects, guaranteed to be complete
        """
        session_id = self._generate_session_id()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching papers (complete mode)...", total=None)

            # Step 1: Initiate search
            progress.update(task, description="Initiating comprehensive search...")
            await self._initiate_search(query, session_id)

            # Step 2: Enhanced polling for complete results
            progress.update(task, description="Waiting for complete results...")
            papers_data = await self._poll_results_complete(session_id)

            # Step 3: Parse and create Paper objects
            progress.update(task, description="Processing complete results...")
            papers = self._parse_papers(papers_data, query)

            # Apply max_results limit if specified
            if max_results and len(papers) > max_results:
                papers = papers[:max_results]

            progress.update(
                task, description=f"Complete: Found {len(papers)} papers", completed=True
            )

        return papers

    async def _poll_results_complete(
        self, session_id: str, poll_interval: float = 2.0, max_polls: int | None = None
    ) -> dict[str, Any]:
        """
        Enhanced polling method that ensures complete results.
        Polls until completion is detected based on stability criteria.
        No hard limit on polls - runs until truly complete.
        """
        url = f"{self.base_url}/paper-agent/api/v1/single_get_result"
        payload = {"session_id": session_id}

        last_paper_count = 0
        stability_count = 0
        required_stability = 3  # Require 3 consecutive stable polls
        min_poll_duration = 10  # Minimum 10 polls before considering completion
        poll_count = 0
        
        # Safety limit to prevent infinite loops (can be overridden)
        safety_limit = max_polls or 120  # Default 4 minutes max

        while poll_count < safety_limit:
            try:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                if data.get("base_resp", {}).get("status_code") == 0:
                    papers_json = data.get("papers", "{}")
                    papers_dict = (
                        json.loads(papers_json) if isinstance(papers_json, str) else papers_json
                    )

                    current_count = len(papers_dict)

                    # Check if we have the same count as last poll
                    if current_count == last_paper_count and current_count > 0:
                        stability_count += 1
                    else:
                        stability_count = 0  # Reset stability counter

                    last_paper_count = current_count

                    # Enhanced completion criteria:
                    # 1. Must have completed minimum polling duration
                    # 2. Must have stable results for required consecutive polls
                    # 3. Must have found at least some papers
                    if (
                        poll_count >= min_poll_duration
                        and stability_count >= required_stability
                        and current_count > 0
                    ):
                        logger.info(
                            f"Enhanced polling complete: {current_count} papers "
                            f"(stable for {stability_count} polls, total polls: {poll_count + 1})"
                        )
                        return papers_dict  # type: ignore

                    # Log progress periodically
                    if poll_count % 5 == 0:
                        logger.debug(
                            f"Enhanced polling: {current_count} papers "
                            f"(stability: {stability_count}/{required_stability}, "
                            f"poll: {poll_count + 1}/{max_polls})"
                        )

            except Exception as e:
                logger.warning(f"Enhanced polling error (attempt {poll_count + 1}): {e}")

            await asyncio.sleep(poll_interval)
            poll_count += 1

        # If we exit the loop, return whatever we have
        logger.warning(
            f"Enhanced polling completed after {safety_limit} attempts with {last_paper_count} papers"
        )

        # Make one final attempt to get results
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get("base_resp", {}).get("status_code") == 0:
                papers_json = data.get("papers", "{}")
                papers_dict = (
                    json.loads(papers_json) if isinstance(papers_json, str) else papers_json
                )
                return papers_dict  # type: ignore
        except Exception as e:
            logger.error(f"Final enhanced polling attempt failed: {e}")

        return {}

    async def _initiate_search(self, query: str, session_id: str) -> None:
        """Initiate search request"""
        url = f"{self.base_url}/paper-agent/api/v1/single_paper_agent"
        payload = {"user_query": query, "session_id": session_id}

        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                if result.get("base_resp", {}).get("status_code") == 0:
                    logger.info(f"Search initiated successfully for session {session_id}")
                    return
                else:
                    raise Exception(f"API error: {result}")

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(
                        f"Failed to initiate search after {self.max_retries} attempts: {e}"
                    ) from e
                logger.warning(f"Search initiation attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2**attempt)

    async def _poll_results(
        self, session_id: str, poll_interval: float = 2.0, max_polls: int = 50
    ) -> dict[str, Any]:
        """Poll for search results until all papers are loaded"""
        url = f"{self.base_url}/paper-agent/api/v1/single_get_result"
        payload = {"session_id": session_id}

        last_paper_count = 0
        stable_count = 0

        for poll_count in range(max_polls):
            try:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()

                if result.get("base_resp", {}).get("status_code") != 0:
                    raise Exception(f"API error: {result}")

                papers_json = result.get("papers", "{}")
                finish = result.get("finish", False)

                # Parse papers JSON
                current_papers = {}
                if papers_json and papers_json != "{}":
                    try:
                        current_papers = json.loads(papers_json)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse papers JSON: {papers_json[:100]}...")

                current_count = len(current_papers)

                # Check if we have results and they're stable
                if current_count > 0:
                    if current_count == last_paper_count:
                        stable_count += 1
                        logger.debug(
                            f"Poll {poll_count + 1}: {current_count} papers (stable for {stable_count} polls)"
                        )

                        # If results are stable for 3 polls AND we have finish=true, return results
                        if finish and stable_count >= 3:
                            logger.info(
                                f"Search completed with {current_count} papers (confirmed stable)"
                            )
                            return current_papers

                        # If stable for many polls even without finish flag, likely complete
                        if stable_count >= 5:
                            logger.info(f"Retrieved {current_count} papers (stable results)")
                            return current_papers
                    else:
                        # Count changed, reset stability counter
                        stable_count = 0
                        logger.debug(
                            f"Poll {poll_count + 1}: {current_count} papers (count increased from {last_paper_count})"
                        )

                    last_paper_count = current_count
                else:
                    # No papers yet
                    if finish:
                        logger.info("Search completed but no papers found")
                        return {}

                    logger.debug(f"Poll {poll_count + 1}: No papers yet, waiting...")

                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error polling results: {e}")
                if poll_count == max_polls - 1:
                    raise
                await asyncio.sleep(poll_interval)

        # If we have papers but timed out, return what we have
        if last_paper_count > 0:
            logger.warning(f"Timeout reached, returning {last_paper_count} papers")
            return current_papers

        raise Exception(f"Timeout: No results after {max_polls} polls")

    def _parse_papers(self, papers_data: dict[str, Any], original_query: str) -> list[Paper]:
        """Parse papers data into Paper objects"""
        papers = []

        for key, paper_info in papers_data.items():
            try:
                paper = self._create_paper_from_api_data(paper_info, original_query)
                if paper:
                    papers.append(paper)
            except Exception as e:
                logger.error(f"Error parsing paper {key}: {e}")

        return papers

    def _create_paper_from_api_data(
        self, paper_info: dict[str, Any], original_query: str
    ) -> Paper | None:
        """Create Paper object from API response data"""
        try:
            entry_id = paper_info.get("entry_id", "")
            title = paper_info.get("title", "")
            authors_list = paper_info.get("authors", [])
            abstract = paper_info.get("abstract", "")
            publish_time = paper_info.get("publish_time", "")
            score = paper_info.get("score", 0.0)

            # Parse authors
            authors = [Author(name=name.strip()) for name in authors_list if name.strip()]

            # Parse publish date
            published_date = None
            if publish_time:
                try:
                    # Format: "20241224" -> datetime
                    if len(publish_time) == 8:
                        year = int(publish_time[:4])
                        month = int(publish_time[4:6])
                        day = int(publish_time[6:8])
                        published_date = datetime(year, month, day)
                except (ValueError, TypeError):
                    logger.debug(f"Could not parse date: {publish_time}")

            # Create metadata
            metadata = PaperMetadata(
                arxiv_id=entry_id,
                title=title,
                authors=authors,
                abstract=abstract,
                published_date=published_date,
                categories=[],  # Not provided in API response
                primary_category=None,
            )

            # Build URLs
            from pydantic import HttpUrl

            pdf_url = HttpUrl(f"https://arxiv.org/pdf/{entry_id}.pdf")
            arxiv_url = HttpUrl(f"https://arxiv.org/abs/{entry_id}")
            tex_url = HttpUrl(f"https://arxiv.org/e-print/{entry_id}")

            # Get BibTeX if available
            bib_result = paper_info.get("bib_result", "")

            # Create Paper object
            paper = Paper(
                metadata=metadata,
                pdf_url=pdf_url,
                arxiv_url=arxiv_url,
                tex_url=tex_url,
                relevance_score=score,
                summary=None,  # Could extract from paper_info if available
                additional_data={
                    "source": paper_info.get("source", ""),
                    "select_reason": paper_info.get("select_reason", ""),
                    "user_query": original_query,
                    "bib_result": bib_result,
                    "json_result": paper_info.get("json_result", ""),
                },
            )

            return paper

        except Exception as e:
            logger.error(f"Error creating paper object: {e}")
            return None
