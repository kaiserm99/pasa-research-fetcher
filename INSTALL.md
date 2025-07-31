# Installation Guide

This guide covers how to install, build, and publish the PASA Research Fetcher package.

## Installation

### From PyPI (Recommended)

Once published, you can install the package directly from PyPI:

```bash
pip install pasa-research-fetcher
```

### From Source

#### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

#### Install uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

#### Clone and Install

```bash
# Clone the repository
git clone https://github.com/marcokaiser/pasa-research-fetcher.git
cd pasa-research-fetcher

# Install dependencies and the package
uv sync

# Install in development mode
uv pip install -e .
```

## Building the Package

### Build Distribution Files

```bash
# Build wheel and sdist
uv build

# The built files will be in the dist/ directory
ls dist/
# pasa_research_fetcher-0.1.0-py3-none-any.whl
# pasa_research_fetcher-0.1.0.tar.gz
```

### Verify Build

```bash
# Test the built wheel
uv pip install dist/pasa_research_fetcher-0.1.0-py3-none-any.whl

# Test import
python -c "import pasa_research_fetcher; print('✓ Package installed successfully')"
```

## Publishing

### Prerequisites for Publishing

1. Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. Generate API tokens:
   - Go to your account settings
   - Create an API token for publishing

3. Configure uv with your credentials:

```bash
# For TestPyPI (testing)
uv publish --repository testpypi --username __token__ --password your-testpypi-token

# For PyPI (production)
uv publish --username __token__ --password your-pypi-token
```

### Publishing Process

#### 1. Test on TestPyPI First

```bash
# Build the package
uv build

# Upload to TestPyPI
uv publish --repository testpypi

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pasa-research-fetcher
```

#### 2. Publish to PyPI

```bash
# Make sure everything works on TestPyPI first
# Then publish to production PyPI
uv build
uv publish
```

### Version Management

Update version in `pyproject.toml` before publishing:

```toml
[project]
name = "pasa-research-fetcher"
version = "0.1.1"  # Update this
# ... rest of config
```

## Development Setup

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/marcokaiser/pasa-research-fetcher.git
cd pasa-research-fetcher

# Install in development mode with dev dependencies
uv sync --dev

# Install pre-commit hooks (optional)
uv run pre-commit install
```

### Running Tests

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio pytest-cov

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=pasa_research_fetcher --cov-report=html
```

### Code Quality

```bash
# Install quality tools
uv add --dev black ruff mypy

# Format code
uv run black src/

# Lint code  
uv run ruff check src/

# Type checking
uv run mypy src/
```

## Using in Other Projects

### As a Dependency

Add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "pasa-research-fetcher>=0.1.0",
]
```

Or install directly:

```bash
# With pip
pip install pasa-research-fetcher

# With uv
uv add pasa-research-fetcher
```

### Basic Usage Examples

#### Simple Search

```python
from pasa_research_fetcher import search_papers_sync

# Synchronous usage
papers = search_papers_sync("transformer neural networks", max_results=5)
for paper in papers:
    print(f"{paper.metadata.title} - {paper.pdf_url}")
```

#### Async Usage

```python
import asyncio
from pasa_research_fetcher import search_papers

async def main():
    papers = await search_papers("attention mechanism", max_results=10)
    for paper in papers:
        print(f"{paper.metadata.title}")

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

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure the package is properly installed
   ```bash
   uv pip list | grep pasa-research-fetcher
   ```

2. **Network Issues**: Check internet connection and firewall settings

3. **Permission Errors**: Use virtual environments to avoid permission issues

4. **Version Conflicts**: Use fresh virtual environment:
   ```bash
   uv venv --python 3.12
   source .venv/bin/activate  # On Unix
   # or .venv\Scripts\activate  # On Windows
   uv pip install pasa-research-fetcher
   ```

### Getting Help

- Check the [GitHub Issues](https://github.com/marcokaiser/pasa-research-fetcher/issues)
- Read the [documentation](https://github.com/marcokaiser/pasa-research-fetcher/docs)
- Review the example scripts in the repository