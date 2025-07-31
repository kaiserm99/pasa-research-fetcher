# PASA Research Fetcher

A professional Python package for fetching and extracting research papers from [pasa-agent.ai](https://pasa-agent.ai/). This tool allows you to search for academic papers, extract their metadata, and download PDF and TeX source files with concurrent processing.

## Features

- 🔍 **Query-based Search**: Search for research papers using natural language queries
- 🤖 **Direct API Access**: Uses PASA's internal API for fast and reliable results
- 📄 **Comprehensive Extraction**: Extracts titles, authors, abstracts, dates, and metadata
- 📚 **ArXiv Integration**: Direct links to ArXiv papers and metadata
- ⬇️ **Concurrent Downloads**: Download PDFs and TeX files with multithreading
- 🎯 **Smart Caching**: Built-in caching to optimize repeated queries
- 🖥️ **CLI Interface**: Easy-to-use command-line interface
- 📊 **Multiple Output Formats**: JSON and table output formats
- 🔧 **Service Integration**: Simple functions for integration into other services

## Installation

```bash
# Install from PyPI (when published)
pip install pasa-research-fetcher

# Or install from source
git clone https://github.com/marcokaiser/pasa-research-fetcher
cd pasa-research-fetcher
uv sync
```

## Quick Start

### Command Line Usage

```bash
# Search for papers and display results
pasa-fetcher "Show me research on long video description"

# Download PDFs and limit results
pasa-fetcher "large language models in-context learning" --max 10 --output ./papers

# Display results in table format
pasa-fetcher "multimodal foundation models" --format table --no-pdfs
```

### Python API Usage

#### Simple Synchronous Usage

```python
from pasa_research_fetcher import search_papers_sync

# Search for papers
papers = search_papers_sync("attention mechanism neural networks", max_results=5)

for paper in papers:
    print(f"Title: {paper.metadata.title}")
    print(f"Authors: {[a.name for a in paper.metadata.authors]}")
    print(f"ArXiv: {paper.arxiv_url}")
    print(f"PDF: {paper.pdf_url}")
    print("---")
```

#### Async Usage

```python
import asyncio
from pasa_research_fetcher import search_papers

async def main():
    papers = await search_papers("transformer neural networks", max_results=10)
    
    for paper in papers:
        print(f"{paper.metadata.title} - Score: {paper.relevance_score:.3f}")

asyncio.run(main())
```

#### Search and Download

```python
from pasa_research_fetcher import search_and_download_sync

result = search_and_download_sync(
    "deep learning",
    output_dir="./papers",
    max_results=3,
    download_pdfs=True
)

print(f"Found {len(result['papers'])} papers")
print(f"Downloads: {result['downloads']}")
```

#### Get Metadata Only

```python
from pasa_research_fetcher import get_paper_metadata_sync
import json

metadata = get_paper_metadata_sync("machine learning", max_results=5)
print(json.dumps(metadata, indent=2, default=str))
```

## Configuration

```python
from pasa_research_fetcher import PasaFetcher, FetcherConfig

config = FetcherConfig(
    timeout=45000,                    # Request timeout in milliseconds
    max_concurrent_downloads=5,       # Concurrent download limit
    download_pdfs=True,               # Download PDF files
    download_tex=False,               # Download TeX source files
    cache_enabled=True,               # Enable caching
    cache_ttl=3600                    # Cache TTL in seconds
)

async with PasaFetcher(config) as fetcher:
    papers = await fetcher.fetch_papers("your query")
```

## CLI Commands

### Search Command

```bash
pasa-fetcher search "your query" [OPTIONS]
```

**Options:**
- `--max, -m`: Maximum number of results
- `--output, -o`: Output directory for downloads
- `--format, -f`: Output format (json, table)
- `--pdfs/--no-pdfs`: Download PDF files
- `--tex/--no-tex`: Download TeX source files
- `--timeout`: Request timeout in milliseconds

### Other Commands

```bash
# Show configuration
pasa-fetcher config

# Show version
pasa-fetcher version
```

## Example Queries

Try these example queries:

- `"Show me research on the long video description. Here, long videos are defined as those with a duration of at least several minutes."`
- `"Give me papers that share some insights about how large language models gain in-context learning capability in the process of pre-training."`
- `"I am looking for research papers on the construction of multimodal foundation models that support both visual and audio inputs and are pre-trained on large-scale datasets."`

## Output Structure

Each paper contains comprehensive metadata:

```json
{
  "metadata": {
    "arxiv_id": "2301.00001",
    "title": "Paper Title",
    "authors": [{"name": "Author Name", "affiliation": "Institution"}],
    "abstract": "Paper abstract...",
    "published_date": "2023-01-01T00:00:00",
    "categories": ["cs.CV", "cs.AI"],
    "primary_category": "cs.CV"
  },
  "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf",
  "arxiv_url": "https://arxiv.org/abs/2301.00001",
  "tex_url": "https://arxiv.org/e-print/2301.00001",
  "relevance_score": 0.95,
  "summary": "PASA-generated summary...",
  "extracted_at": "2024-01-01T12:00:00"
}
```

## Integration Examples

### Service Integration

```python
from pasa_research_fetcher import search_papers
import asyncio

class ResearchService:
    async def get_papers_for_topic(self, topic: str, limit: int = 10):
        papers = await search_papers(topic, max_results=limit)
        return [
            {
                "id": paper.metadata.arxiv_id,
                "title": paper.metadata.title,
                "authors": [a.name for a in paper.metadata.authors],
                "pdf_url": str(paper.pdf_url),
                "relevance_score": paper.relevance_score,
            }
            for paper in papers
        ]

# Usage
service = ResearchService()
papers = await service.get_papers_for_topic("neural networks", limit=5)
```

## Building and Publishing

### Development Setup

```bash
# Clone repository
git clone https://github.com/marcokaiser/pasa-research-fetcher
cd pasa-research-fetcher

# Install in development mode
uv sync --dev
```

### Building

```bash
# Build the package
uv build

# The built files will be in dist/
ls dist/
# pasa_research_fetcher-0.1.0-py3-none-any.whl
# pasa_research_fetcher-0.1.0.tar.gz
```

### Publishing

```bash
# Test on TestPyPI first
uv publish --repository testpypi

# Then publish to PyPI
uv publish
```

## Requirements

- Python 3.12+
- httpx (for HTTP requests)
- BeautifulSoup4 (for HTML parsing)
- Pydantic (for data validation)
- Rich (for beautiful terminal output)
- Typer (for CLI interface)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://github.com/marcokaiser/pasa-research-fetcher/blob/main/README.md)
2. Search [existing issues](https://github.com/marcokaiser/pasa-research-fetcher/issues)
3. Create a new issue with detailed information

## Disclaimer

This tool is for research and educational purposes. Please respect the terms of service of pasa-agent.ai and ArXiv. Use responsibly and consider rate limiting when making many requests.