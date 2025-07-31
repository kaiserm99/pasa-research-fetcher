"""Command-line interface for PASA Research Fetcher"""

import asyncio
import json

import typer
from rich.console import Console
from rich.table import Table

from .core.fetcher import PasaFetcher
from .models.config import FetcherConfig
from .models.paper import Paper

app = typer.Typer(help="PASA Research Fetcher - Extract research papers from pasa-agent.ai")
console = Console()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query for papers"),
    max_results: int | None = typer.Option(None, "--max", "-m", help="Maximum number of results"),
    output_dir: str = typer.Option(
        "./downloads", "--output", "-o", help="Output directory for downloads"
    ),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format (json, table)"),
    download_pdfs: bool = typer.Option(True, "--pdfs/--no-pdfs", help="Download PDF files"),
    download_tex: bool = typer.Option(False, "--tex/--no-tex", help="Download TeX source files"),
    headless: bool = typer.Option(
        True, "--headless/--no-headless", help="Run browser in headless mode"
    ),
    timeout: int = typer.Option(30000, "--timeout", help="Page load timeout in milliseconds"),
) -> None:
    """Search for research papers and optionally download them"""
    asyncio.run(
        _search_async(
            query,
            max_results,
            output_dir,
            output_format,
            download_pdfs,
            download_tex,
            headless,
            timeout,
        )
    )


async def _search_async(
    query: str,
    max_results: int | None,
    output_dir: str,
    output_format: str,
    download_pdfs: bool,
    download_tex: bool,
    headless: bool,
    timeout: int,
) -> None:
    """Async search implementation"""
    config = FetcherConfig(
        headless=headless, timeout=timeout, download_pdfs=download_pdfs, download_tex=download_tex
    )

    async with PasaFetcher(config) as fetcher:
        console.print(f"[bold blue]Searching for:[/bold blue] {query}")

        papers = await fetcher.fetch_papers(query, max_results)

        if not papers:
            console.print("[yellow]No papers found[/yellow]")
            return

        console.print(f"[green]Found {len(papers)} papers[/green]")

        # Display results
        if output_format == "table":
            _display_table(papers)
        else:
            _display_json(papers)

        # Download papers if requested
        if download_pdfs or download_tex:
            console.print(f"\n[bold blue]Downloading papers to {output_dir}[/bold blue]")
            download_results = await fetcher.download_papers(papers, output_dir)

            success_count = sum(1 for result in download_results.values() if "error" not in result)
            console.print(
                f"[green]Successfully downloaded {success_count}/{len(papers)} papers[/green]"
            )


def _display_table(papers: list[Paper]) -> None:
    """Display papers in a table format"""
    table = Table(title="Research Papers")
    table.add_column("Title", style="cyan", width=50)
    table.add_column("Authors", style="green", width=30)
    table.add_column("ArXiv ID", style="yellow")
    table.add_column("Date", style="magenta")

    for paper in papers:
        authors = ", ".join([author.name for author in paper.metadata.authors[:3]])
        if len(paper.metadata.authors) > 3:
            authors += "..."

        date_str = (
            paper.metadata.published_date.strftime("%Y-%m-%d")
            if paper.metadata.published_date
            else "N/A"
        )

        table.add_row(
            paper.metadata.title[:100] + ("..." if len(paper.metadata.title) > 100 else ""),
            authors,
            paper.metadata.arxiv_id,
            date_str,
        )

    console.print(table)


def _display_json(papers: list[Paper]) -> None:
    """Display papers in JSON format"""
    papers_data = []
    for paper in papers:
        papers_data.append(json.loads(paper.model_dump_json()))

    console.print_json(data=papers_data)


@app.command("search-complete")
def search_complete(
    query: str = typer.Argument(..., help="Search query for papers"),
    max_results: int | None = typer.Option(None, "--max", "-m", help="Maximum number of results"),
    output_dir: str = typer.Option(
        "./downloads", "--output", "-o", help="Output directory for downloads"
    ),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format (json, table)"),
    download_pdfs: bool = typer.Option(True, "--pdfs/--no-pdfs", help="Download PDF files"),
    download_tex: bool = typer.Option(False, "--tex/--no-tex", help="Download TeX source files"),
    sort_by_relevance: bool = typer.Option(True, "--sort/--no-sort", help="Sort by relevance score"),
    timeout: int = typer.Option(60000, "--timeout", help="Request timeout in milliseconds"),
) -> None:
    """Search for research papers with completion guarantee and relevance sorting"""
    asyncio.run(
        _search_complete_async(
            query,
            max_results,
            output_dir,
            output_format,
            download_pdfs,
            download_tex,
            sort_by_relevance,
            timeout,
        )
    )


async def _search_complete_async(
    query: str,
    max_results: int | None,
    output_dir: str,
    output_format: str,
    download_pdfs: bool,
    download_tex: bool,
    sort_by_relevance: bool,
    timeout: int,
) -> None:
    """Internal async function for complete search"""
    config = FetcherConfig(
        timeout=timeout,
        download_pdfs=download_pdfs,
        download_tex=download_tex,
    )

    async with PasaFetcher(config) as fetcher:
        # Use the complete search method
        papers = await fetcher.fetch_papers_until_complete(
            query, max_results, sort_by_relevance
        )

        if not papers:
            console.print("[yellow]No papers found for query.[/yellow]")
            return

        # Download files if requested
        if download_pdfs or download_tex:
            await fetcher.download_papers(papers, output_dir)

        # Format and display results
        if output_format == "table":
            _display_table(papers)
        else:
            _display_json(papers)


@app.command()
def config() -> None:
    """Show current configuration"""
    config = FetcherConfig()
    console.print_json(data=config.model_dump())


@app.command()
def version() -> None:
    """Show version information"""
    from . import __version__

    console.print(f"PASA Research Fetcher v{__version__}")


if __name__ == "__main__":
    app()
