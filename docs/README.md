# PASA Research Fetcher Documentation

Welcome to the comprehensive documentation for PASA Research Fetcher - a professional Python package for fetching and extracting research papers from [pasa-agent.ai](https://pasa-agent.ai/).

## Quick Navigation

- **[Installation Guide](installation.md)** - Get started with installing the package
- **[API Reference](api-reference.md)** - Complete function and class documentation
- **[CLI Guide](cli-guide.md)** - Command-line interface usage
- **[Examples](examples.md)** - Comprehensive usage examples
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## What is PASA Research Fetcher?

PASA Research Fetcher is a powerful Python package that provides:

- 🔍 **Natural Language Search**: Query research papers using plain English
- 🤖 **Direct API Access**: Uses PASA's internal API for reliable results
- 📄 **Complete Metadata**: Extracts titles, authors, abstracts, and more
- 📚 **ArXiv Integration**: Direct links to papers and sources
- ⬇️ **Concurrent Downloads**: Download PDFs and TeX files efficiently
- 🎯 **Smart Caching**: Built-in performance optimization
- 🖥️ **CLI Interface**: Easy command-line usage
- 🔧 **Service Integration**: Simple API for embedding in applications

## Quick Start

### Installation
```bash
pip install pasa-research-fetcher
```

### Basic Usage
```python
from pasa_research_fetcher import search_papers_sync

papers = search_papers_sync("attention mechanism neural networks", max_results=10)
for paper in papers:
    print(f"{paper.metadata.title} - Score: {paper.relevance_score:.3f}")
```

### Command Line
```bash
pasa-fetcher search "machine learning transformers" --format table --max 10
```

## Key Features

### 🔍 Natural Language Queries
Search using descriptive queries like:
- "Show me research on long video description with duration of several minutes"
- "Papers about how large language models gain in-context learning capability"
- "Multimodal foundation models supporting visual and audio inputs"

### 📊 Complete Results
The package implements smart polling to ensure you get complete results, not partial ones. It waits for the "All Papers Found" indicator from PASA.

### 🚀 Multiple Usage Patterns

**Synchronous (Simple)**
```python
from pasa_research_fetcher import search_papers_sync
papers = search_papers_sync("deep learning", max_results=20)
```

**Asynchronous (Scalable)**
```python
from pasa_research_fetcher import search_papers
papers = await search_papers("computer vision", max_results=50)
```

**Service Integration**
```python
from pasa_research_fetcher import PasaFetcher, FetcherConfig

config = FetcherConfig(timeout=60000, cache_ttl=3600)
async with PasaFetcher(config) as fetcher:
    papers = await fetcher.fetch_papers("neural networks")
```

## Documentation Structure

### For New Users
1. Start with [Installation](installation.md)
2. Read the [Examples](examples.md) for your use case
3. Check [CLI Guide](cli-guide.md) for command-line usage

### For Developers
1. Review [API Reference](api-reference.md) for detailed function documentation
2. Study [Examples](examples.md) for integration patterns
3. Use [Troubleshooting](troubleshooting.md) when needed

### For Service Integration
1. See [Examples](examples.md) → Service Integration section
2. Check [API Reference](api-reference.md) for configuration options
3. Review performance considerations in [Troubleshooting](troubleshooting.md)

## Example Use Cases

### Academic Research
- Literature reviews and surveys
- Finding papers for specific research topics
- Building comprehensive bibliographies
- Tracking research trends

### Development Integration
- Research-aware applications
- Academic search APIs
- Automated paper collection
- Research recommendation systems

### Data Analysis
- Research trend analysis
- Author collaboration networks
- Citation pattern studies
- Academic productivity metrics

## Support and Community

- **Issues**: [GitHub Issues](https://github.com/kaiserm99/pasa-research-fetcher/issues)
- **Documentation**: You're reading it! 📖
- **Examples**: Check the [examples directory](https://github.com/kaiserm99/pasa-research-fetcher/tree/main/examples)

## Requirements

- Python 3.12+
- Internet connection (for API access)
- Optional: Additional disk space for PDF downloads

## License

MIT License - feel free to use in your projects, both commercial and non-commercial.

---

**Ready to get started?** Head to the [Installation Guide](installation.md) to begin using PASA Research Fetcher in your projects!