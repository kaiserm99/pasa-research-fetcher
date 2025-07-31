"""Paper downloader with concurrent support"""

import asyncio
from pathlib import Path

import httpx
from asyncio_throttle.throttler import Throttler

from ..models.paper import Paper
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PaperDownloader:
    """Download PDF and TeX files for papers with concurrent support"""

    def __init__(self, max_concurrent: int = 5, output_dir: str = "./downloads"):
        self.max_concurrent = max_concurrent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.AsyncClient(timeout=60.0)
        self.throttler = Throttler(rate_limit=max_concurrent, period=1.0)

    async def download_papers(
        self, papers: list[Paper], download_pdfs: bool = True, download_tex: bool = False
    ) -> dict[str, dict[str, str]]:
        """
        Download papers concurrently

        Args:
            papers: List of Paper objects
            download_pdfs: Whether to download PDF files
            download_tex: Whether to download TeX source files

        Returns:
            Dictionary mapping arxiv_id to file paths
        """
        results = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)

        tasks = []
        for paper in papers:
            task = self._download_paper(paper, semaphore, download_pdfs, download_tex)
            tasks.append(task)

        download_results = await asyncio.gather(*tasks, return_exceptions=True)

        for paper, result in zip(papers, download_results, strict=False):
            if isinstance(result, Exception):
                logger.error(f"Error downloading {paper.metadata.arxiv_id}: {result}")
                results[paper.metadata.arxiv_id] = {"error": str(result)}
            else:
                results[paper.metadata.arxiv_id] = result  # type: ignore

        return results

    async def _download_paper(
        self, paper: Paper, semaphore: asyncio.Semaphore, download_pdfs: bool, download_tex: bool
    ) -> dict[str, str]:
        """Download individual paper files"""
        async with semaphore:
            result = {}
            arxiv_id = paper.metadata.arxiv_id

            # Create directory for this paper
            paper_dir = self.output_dir / arxiv_id
            paper_dir.mkdir(exist_ok=True)

            # Download PDF
            if download_pdfs and paper.pdf_url:
                pdf_path = await self._download_file(
                    str(paper.pdf_url), paper_dir / f"{arxiv_id}.pdf"
                )
                if pdf_path:
                    result["pdf"] = str(pdf_path)

            # Download TeX source
            if download_tex and paper.tex_url:
                tex_path = await self._download_file(
                    str(paper.tex_url), paper_dir / f"{arxiv_id}.tar.gz"
                )
                if tex_path:
                    result["tex"] = str(tex_path)

            # Save metadata
            metadata_path = paper_dir / f"{arxiv_id}_metadata.json"
            try:
                with open(metadata_path, "w") as f:
                    f.write(paper.model_dump_json(indent=2))
                result["metadata"] = str(metadata_path)
            except Exception as e:
                logger.error(f"Error saving metadata for {arxiv_id}: {e}")

            return result

    async def _download_file(self, url: str, filepath: Path) -> Path | None:
        """Download a single file with throttling"""
        try:
            async with self.throttler:
                logger.info(f"Downloading {url} to {filepath}")

                response = await self.client.get(url, follow_redirects=True)
                response.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(response.content)

                logger.info(f"Successfully downloaded {filepath}")
                return filepath

        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None

    async def close(self) -> None:
        """Close HTTP client"""
        await self.client.aclose()
