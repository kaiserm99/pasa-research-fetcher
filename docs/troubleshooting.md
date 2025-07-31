# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Python Version Error
```
ERROR: Package requires Python >=3.12
```

**Solution:**
```bash
# Check your Python version
python --version

# Install Python 3.12+ if needed
# On Ubuntu/Debian:
sudo apt update && sudo apt install python3.12

# On macOS with Homebrew:
brew install python@3.12

# On Windows: Download from python.org
```

#### Permission Denied Errors
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Install for current user only
pip install --user pasa-research-fetcher

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pasa-research-fetcher
```

#### Package Not Found
```
ERROR: No matching distribution found for pasa-research-fetcher
```

**Solution:**
```bash
# Update pip first
pip install --upgrade pip

# Try installing from source
pip install git+https://github.com/kaiserm99/pasa-research-fetcher.git
```

### Runtime Issues

#### Network Connection Errors
```
httpx.ConnectError: Connection failed
```

**Possible Causes & Solutions:**

1. **No Internet Connection**
   - Check your internet connection
   - Try accessing https://pasa-agent.ai in browser

2. **Corporate Firewall/Proxy**
   ```bash
   # Set proxy environment variables
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   
   # Or configure pip proxy
   pip install --proxy http://proxy.company.com:8080 pasa-research-fetcher
   ```

3. **DNS Issues**
   ```bash
   # Try different DNS servers
   # Add to /etc/resolv.conf (Linux) or change network settings
   nameserver 8.8.8.8
   nameserver 8.8.4.4
   ```

#### Timeout Errors
```
httpx.ReadTimeout: Read timeout
```

**Solution:**
```python
from pasa_research_fetcher import FetcherConfig, PasaFetcher

# Increase timeout
config = FetcherConfig(timeout=60000)  # 60 seconds
```

Or with CLI:
```bash
pasa-fetcher search "your query" --timeout 60000
```

#### SSL Certificate Errors
```
ssl.SSLCertVerifyError: certificate verify failed
```

**Solution:**
```bash
# Update certificates (macOS)
/Applications/Python\ 3.12/Install\ Certificates.command

# On Linux, update ca-certificates
sudo apt update && sudo apt install ca-certificates

# As last resort (not recommended for production)
# Set environment variable to skip SSL verification
export PYTHONHTTPSVERIFY=0
```

### CLI Issues

#### Command Not Found
```
pasa-fetcher: command not found
```

**Solutions:**

1. **Check Installation**
   ```bash
   pip show pasa-research-fetcher
   ```

2. **Add to PATH**
   ```bash
   # Find where pip installs binaries
   python -m site --user-base
   
   # Add to PATH (add to ~/.bashrc or ~/.zshrc)
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Run Directly**
   ```bash
   python -m pasa_research_fetcher.cli search "your query"
   ```

#### JSON Parsing Errors
```
json.JSONDecodeError: Expecting value
```

**Solution:**
This usually indicates network issues or API changes. Try:

```bash
# Use table format instead
pasa-fetcher search "your query" --format table

# Check with simple query first
pasa-fetcher search "machine learning" --max 1
```

### Performance Issues

#### Slow Response Times
```
Search taking longer than expected...
```

**Solutions:**

1. **Reduce Result Count**
   ```bash
   pasa-fetcher search "broad query" --max 10
   ```

2. **Increase Timeout**
   ```bash
   pasa-fetcher search "complex query" --timeout 90000
   ```

3. **Check Query Specificity**
   - More specific queries return faster
   - Avoid very broad terms like "AI" or "machine learning" alone

#### Memory Issues
```
MemoryError: Unable to allocate memory
```

**Solutions:**

1. **Reduce Concurrent Downloads**
   ```python
   config = FetcherConfig(max_concurrent_downloads=1)
   ```

2. **Process in Batches**
   ```python
   # Instead of fetching 1000 papers at once
   for i in range(0, 1000, 50):
       papers = search_papers_sync(query, max_results=50)
       process_papers(papers)
   ```

### API Issues

#### No Results Returned
```
Found 0 papers for query: "your query"
```

**Troubleshooting Steps:**

1. **Check Query Format**
   ```bash
   # Good queries
   pasa-fetcher search "attention mechanism transformers"
   pasa-fetcher search "computer vision object detection"
   
   # Avoid very short or generic queries
   pasa-fetcher search "AI"  # Too generic
   ```

2. **Test with Known Working Queries**
   ```bash
   pasa-fetcher search "neural networks" --max 5
   ```

3. **Check PASA Website**
   - Visit https://pasa-agent.ai directly
   - Try the same query there

#### Partial Results
```
Only getting 3-5 papers instead of many
```

This was fixed in recent versions, but if you still see this:

1. **Update Package**
   ```bash
   pip install --upgrade pasa-research-fetcher
   ```

2. **Increase Timeout**
   ```bash
   pasa-fetcher search "your query" --timeout 60000
   ```

### File Download Issues

#### Permission Denied When Saving Files
```
PermissionError: [Errno 13] Permission denied: './papers/2301.00001.pdf'
```

**Solutions:**

1. **Check Directory Permissions**
   ```bash
   mkdir -p ./papers
   chmod 755 ./papers
   ```

2. **Use Different Output Directory**
   ```bash
   pasa-fetcher search "query" --pdfs --output ~/Downloads/papers
   ```

#### Incomplete Downloads
```
Downloaded files are corrupted or incomplete
```

**Solutions:**

1. **Check Disk Space**
   ```bash
   df -h
   ```

2. **Reduce Concurrent Downloads**
   ```python
   config = FetcherConfig(max_concurrent_downloads=2)
   ```

3. **Check Network Stability**
   - Try downloading one paper at a time
   - Use wired connection if on WiFi

### Import Issues

#### ModuleNotFoundError
```python
ModuleNotFoundError: No module named 'pasa_research_fetcher'
```

**Solutions:**

1. **Check Installation**
   ```bash
   pip list | grep pasa
   ```

2. **Virtual Environment Issues**
   ```bash
   # Make sure you're in the right environment
   which python
   which pip
   
   # Reinstall in current environment
   pip install pasa-research-fetcher
   ```

3. **Development Installation**
   ```bash
   # If installing from source
   cd pasa-research-fetcher
   pip install -e .
   ```

#### Import Warnings
```
DeprecationWarning: json_encoders is deprecated
```

These are harmless warnings from Pydantic v2 transition. To hide them:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from pasa_research_fetcher import search_papers_sync
```

### Debugging Tips

#### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your code here - will show detailed logs
```

#### Check Package Version
```bash
pasa-fetcher version
# or
python -c "import pasa_research_fetcher; print(pasa_research_fetcher.__version__)"
```

#### Test Basic Functionality
```python
# Minimal test
from pasa_research_fetcher import search_papers_sync

try:
    papers = search_papers_sync("test", max_results=1)
    print(f"✅ Found {len(papers)} papers")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Getting Help

If none of these solutions work:

1. **Check GitHub Issues**
   - Search [existing issues](https://github.com/kaiserm99/pasa-research-fetcher/issues)
   - Look for similar problems and solutions

2. **Create New Issue**
   Include:
   - Python version (`python --version`)
   - Package version (`pasa-fetcher version`)
   - Operating system
   - Full error message
   - Steps to reproduce

3. **Environment Information**
   ```bash
   # Gather system info
   python --version
   pip list | grep -E "(pasa|httpx|pydantic|rich|typer)"
   uname -a  # On Linux/macOS
   ```

4. **Minimal Reproduction Case**
   Create the smallest possible code example that reproduces the issue.

## Known Limitations

1. **Rate Limiting**: PASA may limit requests from the same IP
2. **Query Complexity**: Very complex queries may timeout
3. **Network Dependencies**: Requires stable internet connection
4. **ArXiv Access**: Some features depend on ArXiv being accessible