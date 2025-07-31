# Installation Guide

## Requirements

- Python 3.12 or higher
- pip or uv package manager (recommended)

## Installation Methods

### From PyPI (Recommended)

```bash
pip install pasa-research-fetcher
```

Or using uv (faster):

```bash
uv add pasa-research-fetcher
```

### From Source

```bash
# Clone the repository
git clone https://github.com/kaiserm99/pasa-research-fetcher.git
cd pasa-research-fetcher

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Development Installation

```bash
# Clone and install with development dependencies
git clone https://github.com/kaiserm99/pasa-research-fetcher.git
cd pasa-research-fetcher
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

## Verify Installation

After installation, verify everything works:

```bash
# Test CLI
pasa-fetcher --help

# Test Python import
python -c "from pasa_research_fetcher import search_papers_sync; print('✅ Installation successful')"
```

## Dependencies

The package automatically installs these core dependencies:

- **httpx**: HTTP client for API requests
- **beautifulsoup4**: HTML parsing for ArXiv metadata
- **lxml**: Fast XML/HTML parser
- **pydantic**: Data validation and models
- **rich**: Beautiful terminal output
- **typer**: CLI framework

### Optional Dependencies

For enhanced download functionality:

```bash
pip install pasa-research-fetcher[download]
```

This adds:
- **asyncio-throttle**: Rate limiting for concurrent downloads

## Troubleshooting

### Common Issues

1. **Python Version Error**
   - Ensure you have Python 3.12 or higher: `python --version`

2. **Permission Errors on Linux/macOS**
   ```bash
   pip install --user pasa-research-fetcher
   ```

3. **Network/Proxy Issues**
   - Configure your proxy settings if behind a corporate firewall
   - Some features may require direct internet access to PASA and ArXiv

4. **Import Errors**
   - Try reinstalling: `pip uninstall pasa-research-fetcher && pip install pasa-research-fetcher`
   - Check for conflicting packages in your environment

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search [existing issues](https://github.com/kaiserm99/pasa-research-fetcher/issues)
3. Create a new issue with your system details and error messages