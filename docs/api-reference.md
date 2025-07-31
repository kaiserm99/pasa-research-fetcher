# API Reference

## Core Functions

### `search_papers_sync(query, max_results=50, config=None)`

Synchronous function to search for research papers.

**Parameters:**
- `query` (str): Natural language research query
- `max_results` (int, optional): Maximum number of papers to return. Default: 50
- `config` (FetcherConfig, optional): Custom configuration object

**Returns:**
- `List[Paper]`: List of Paper objects with metadata and URLs

**Example:**
```python
from pasa_research_fetcher import search_papers_sync

papers = search_papers_sync("attention mechanism neural networks", max_results=10)
for paper in papers:
    print(f"{paper.metadata.title} - Score: {paper.relevance_score}")
```

### `search_papers(query, max_results=50, config=None)`

Asynchronous version of `search_papers_sync`.

**Parameters:** Same as `search_papers_sync`

**Returns:** Same as `search_papers_sync`

**Example:**
```python
import asyncio
from pasa_research_fetcher import search_papers

async def main():
    papers = await search_papers("transformer neural networks", max_results=5)
    return papers

papers = asyncio.run(main())
```

### `get_paper_metadata_sync(query, max_results=50)`

Synchronous function to get only paper metadata (no full Paper objects).

**Parameters:**
- `query` (str): Natural language research query
- `max_results` (int, optional): Maximum number of papers. Default: 50

**Returns:**
- `List[Dict[str, Any]]`: List of dictionaries with paper metadata

**Example:**
```python
from pasa_research_fetcher import get_paper_metadata_sync
import json

metadata = get_paper_metadata_sync("machine learning", max_results=3)
print(json.dumps(metadata, indent=2, default=str))
```

### `get_paper_metadata(query, max_results=50)`

Asynchronous version of `get_paper_metadata_sync`.

### `search_and_download_sync(query, output_dir, max_results=50, download_pdfs=True, download_tex=False)`

Synchronous function to search and download papers in one step.

**Parameters:**
- `query` (str): Natural language research query
- `output_dir` (str): Directory to save downloaded files
- `max_results` (int, optional): Maximum number of papers. Default: 50
- `download_pdfs` (bool, optional): Download PDF files. Default: True
- `download_tex` (bool, optional): Download TeX source files. Default: False

**Returns:**
- `Dict[str, Any]`: Dictionary with 'papers' and 'downloads' keys

**Example:**
```python
from pasa_research_fetcher import search_and_download_sync

result = search_and_download_sync(
    "deep learning computer vision",
    output_dir="./papers",
    max_results=5,
    download_pdfs=True
)

print(f"Found {len(result['papers'])} papers")
print(f"Downloads: {result['downloads']}")
```

## Core Classes

### `PasaFetcher`

Main class for advanced usage with custom configuration.

**Constructor:**
```python
PasaFetcher(config: FetcherConfig = None)
```

**Methods:**

#### `async fetch_papers(query: str) -> List[Paper]`
Fetch papers for a given query.

#### `async download_papers(papers: List[Paper], output_dir: str) -> Dict[str, Dict[str, str]]`
Download PDF/TeX files for papers.

**Example:**
```python
import asyncio
from pasa_research_fetcher import PasaFetcher, FetcherConfig

async def main():
    config = FetcherConfig(timeout=60000, cache_ttl=7200)
    
    async with PasaFetcher(config) as fetcher:
        papers = await fetcher.fetch_papers("quantum computing")
        downloads = await fetcher.download_papers(papers, "./downloads")
        return papers, downloads

papers, downloads = asyncio.run(main())
```

### `FetcherConfig`

Configuration class for customizing fetcher behavior.

**Parameters:**
- `timeout` (int): Request timeout in milliseconds. Default: 30000
- `max_concurrent_downloads` (int): Max concurrent downloads. Default: 3
- `download_pdfs` (bool): Download PDF files by default. Default: False
- `download_tex` (bool): Download TeX files by default. Default: False
- `cache_enabled` (bool): Enable result caching. Default: True
- `cache_ttl` (int): Cache time-to-live in seconds. Default: 3600

**Example:**
```python
from pasa_research_fetcher import FetcherConfig

config = FetcherConfig(
    timeout=45000,
    max_concurrent_downloads=5,
    download_pdfs=True,
    cache_ttl=7200
)
```

## Data Models

### `Paper`

Main paper object containing all information about a research paper.

**Attributes:**
- `metadata` (PaperMetadata): Paper metadata (title, authors, etc.)
- `pdf_url` (HttpUrl): Direct link to PDF file
- `arxiv_url` (HttpUrl): ArXiv abstract page URL  
- `tex_url` (HttpUrl | None): Link to TeX source (if available)
- `relevance_score` (float): PASA relevance score (0.0-1.0)
- `summary` (str | None): PASA-generated summary
- `extracted_at` (datetime): When the paper was extracted

### `PaperMetadata`

Detailed metadata for a research paper.

**Attributes:**
- `arxiv_id` (str): ArXiv identifier (e.g., "2301.00001")
- `title` (str): Paper title
- `authors` (List[Author]): List of authors with affiliations
- `abstract` (str): Paper abstract
- `published_date` (datetime | None): Publication date
- `categories` (List[str]): ArXiv categories (e.g., ["cs.CV", "cs.AI"])
- `primary_category` (str): Primary ArXiv category

### `Author`

Author information.

**Attributes:**
- `name` (str): Author's full name
- `affiliation` (str | None): Author's institution/affiliation

## Error Handling

All functions handle errors gracefully and return empty results on failure. For detailed error information, check the logs:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Your code here - errors will be logged
```

## Rate Limiting

The package includes built-in rate limiting to be respectful to PASA and ArXiv servers:

- API requests are automatically throttled
- Download operations use configurable concurrency limits
- Caching reduces redundant requests

## Thread Safety

All functions are thread-safe. Async functions can be used safely in concurrent contexts:

```python
import asyncio
from pasa_research_fetcher import search_papers

async def search_multiple_topics():
    tasks = [
        search_papers("neural networks", max_results=10),
        search_papers("computer vision", max_results=10),
        search_papers("natural language processing", max_results=10)
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```