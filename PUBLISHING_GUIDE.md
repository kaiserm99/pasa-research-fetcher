# PyPI Publishing Guide for PASA Research Fetcher

This guide walks you through publishing your package to PyPI and setting up automated publishing with GitHub Actions.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org/account/register/)
2. **GitHub Account**: Ensure you have access to create repositories
3. **SSH Keys**: Set up SSH keys for GitHub (you mentioned having this configured)

## Step 1: Set Up PyPI Account

1. Go to [PyPI](https://pypi.org) and create an account
2. Verify your email address
3. Go to [Account Settings > API tokens](https://pypi.org/manage/account/token/)
4. Create a new API token:
   - Name: `pasa-research-fetcher-token`
   - Scope: `Entire account` (initially, can scope to project later)
5. **IMPORTANT**: Copy the token immediately - you won't see it again!

## Step 2: Create GitHub Repository

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: PASA Research Fetcher package

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Create repository on GitHub
gh repo create pasa-research-fetcher --public --push --source=.

# Or manually create on GitHub.com and push:
git remote add origin git@github.com-personal:kaiserm99/pasa-research-fetcher.git
git branch -M main
git push -u origin main
```

## Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (starts with `pypi-`)

## Step 4: Manual Publishing (First Time)

For the first release, publish manually to ensure everything works:

```bash
# Run the publishing script
uv run python publish.py

# Or manually:
uv build
uv run twine upload dist/*
```

When prompted, use:
- Username: `__token__`
- Password: Your PyPI API token

## Step 5: Automated Publishing with Tags

Once manual publishing works, you can use GitHub Actions:

```bash
# Create and push a version tag
git tag v0.1.0
git push origin v0.1.0
```

This will automatically:
1. Run tests
2. Build the package
3. Publish to PyPI

## Step 6: Update Version for Future Releases

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # or whatever the next version is
   ```

2. Commit changes:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.1"
   git push
   ```

3. Create and push tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

## Directory Structure After Setup

```
pasa-research-fetcher/
├── .github/
│   └── workflows/
│       ├── publish.yml     # Auto-publish on tags
│       └── test.yml        # Run tests on PRs
├── src/pasa_research_fetcher/
├── tests/
├── pyproject.toml
├── README.md
├── PUBLISHING_GUIDE.md     # This file
└── publish.py              # Manual publishing script
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure your PyPI token is correct and has the right permissions
2. **Package Name Conflict**: If name is taken, update `name` in `pyproject.toml`
3. **Version Conflict**: Increase version number in `pyproject.toml`

### Testing Your Published Package

```bash
# Install from PyPI
pip install pasa-research-fetcher

# Test CLI
pasa-fetcher --help

# Test in Python
python -c "from pasa_research_fetcher import search_papers_sync; print('✅ Import successful')"
```

## Package Usage After Publishing

Users can install and use your package:

```bash
# Installation
pip install pasa-research-fetcher
# or
uv add pasa-research-fetcher

# CLI Usage
pasa-fetcher search "attention mechanism" --max 5 --pdfs

# Python Usage
from pasa_research_fetcher import search_papers_sync
papers = search_papers_sync("transformer architecture", max_results=10)
```

## Next Steps

1. ✅ Build and test package locally
2. ✅ Set up PyPI account and get API token
3. ✅ Create GitHub repository
4. ✅ Add PyPI token to GitHub secrets
5. 🔄 Run initial manual publish
6. 🔄 Test automated publishing with tags
7. 🔄 Update README with installation instructions

Good luck with your publishing! 🚀