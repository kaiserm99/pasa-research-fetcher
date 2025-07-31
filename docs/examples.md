# Usage Examples

This page provides comprehensive examples of using the PASA Research Fetcher in various scenarios.

## Basic Usage

### Simple Paper Search

```python
from pasa_research_fetcher import search_papers_sync

# Search for papers
papers = search_papers_sync("attention mechanism neural networks", max_results=10)

# Display results
for paper in papers:
    print(f"Title: {paper.metadata.title}")
    print(f"Authors: {[a.name for a in paper.metadata.authors]}")
    print(f"ArXiv: {paper.arxiv_url}")
    print(f"Relevance: {paper.relevance_score:.3f}")
    print("---")
```

### Async Usage

```python
import asyncio
from pasa_research_fetcher import search_papers

async def main():
    papers = await search_papers("transformer neural networks", max_results=5)
    
    for paper in papers:
        print(f"{paper.metadata.title} - Score: {paper.relevance_score:.3f}")
        
    return papers

papers = asyncio.run(main())
```

## Advanced Usage

### Custom Configuration

```python
from pasa_research_fetcher import PasaFetcher, FetcherConfig

async def search_with_config():
    # Create custom configuration
    config = FetcherConfig(
        timeout=60000,                    # 60 second timeout
        max_concurrent_downloads=5,       # 5 concurrent downloads
        download_pdfs=True,               # Download PDFs by default
        cache_ttl=7200                    # 2 hour cache
    )
    
    # Use custom configuration
    async with PasaFetcher(config) as fetcher:
        papers = await fetcher.fetch_papers("deep learning computer vision")
        return papers

papers = asyncio.run(search_with_config())
```

### Search and Download

```python
from pasa_research_fetcher import search_and_download_sync

# Search and download in one step
result = search_and_download_sync(
    "machine learning optimization",
    output_dir="./papers",
    max_results=5,
    download_pdfs=True,
    download_tex=True
)

print(f"Found {len(result['papers'])} papers")
print(f"Downloads: {result['downloads']}")

# Access individual papers
for paper in result['papers']:
    print(f"- {paper.metadata.title}")
```

### Metadata Only

```python
from pasa_research_fetcher import get_paper_metadata_sync
import json

# Get only metadata (lighter, faster)
metadata = get_paper_metadata_sync("quantum computing", max_results=10)

# Pretty print metadata
print(json.dumps(metadata, indent=2, default=str))

# Access specific fields
for paper in metadata:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join([a['name'] for a in paper['authors']])}")
    print(f"Published: {paper['published_date']}")
    print()
```

## Service Integration Examples

### Research Service Class

```python
import asyncio
from typing import List, Dict, Any
from pasa_research_fetcher import search_papers, PasaFetcher, FetcherConfig

class ResearchService:
    def __init__(self):
        self.config = FetcherConfig(
            timeout=45000,
            cache_ttl=3600,
            max_concurrent_downloads=3
        )
    
    async def get_papers_for_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get papers for a research topic"""
        papers = await search_papers(topic, max_results=limit)
        
        return [
            {
                "id": paper.metadata.arxiv_id,
                "title": paper.metadata.title,
                "authors": [a.name for a in paper.metadata.authors],
                "abstract": paper.metadata.abstract,
                "pdf_url": str(paper.pdf_url),
                "arxiv_url": str(paper.arxiv_url),
                "relevance_score": paper.relevance_score,
                "published_date": paper.metadata.published_date,
                "categories": paper.metadata.categories
            }
            for paper in papers
        ]
    
    async def get_similar_papers(self, paper_title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find papers similar to a given paper"""
        # Use the title as a search query
        query = f"similar to: {paper_title}"
        return await self.get_papers_for_topic(query, limit)
    
    async def build_literature_review(self, topics: List[str], papers_per_topic: int = 15) -> Dict[str, List[Dict[str, Any]]]:
        """Build a literature review across multiple topics"""
        results = {}
        
        # Search all topics concurrently
        tasks = [
            self.get_papers_for_topic(topic, papers_per_topic)
            for topic in topics
        ]
        
        topic_results = await asyncio.gather(*tasks)
        
        for topic, papers in zip(topics, topic_results):
            results[topic] = papers
        
        return results

# Usage
async def main():
    service = ResearchService()
    
    # Get papers for a single topic
    ml_papers = await service.get_papers_for_topic("machine learning optimization", limit=10)
    print(f"Found {len(ml_papers)} ML papers")
    
    # Build literature review
    topics = ["attention mechanisms", "transformer architectures", "neural machine translation"]
    review = await service.build_literature_review(topics, papers_per_topic=20)
    
    for topic, papers in review.items():
        print(f"\n{topic.upper()}:")
        for paper in papers[:3]:  # Show top 3
            print(f"  - {paper['title']} (Score: {paper['relevance_score']:.3f})")

asyncio.run(main())
```

### Flask Web API

```python
from flask import Flask, jsonify, request
from pasa_research_fetcher import search_papers_sync, get_paper_metadata_sync
import asyncio

app = Flask(__name__)

@app.route('/api/search', methods=['GET'])
def search_papers_api():
    """API endpoint for searching papers"""
    query = request.args.get('q', '')
    max_results = int(request.args.get('max', 20))
    format_type = request.args.get('format', 'full')
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    try:
        if format_type == 'metadata':
            # Return only metadata
            results = get_paper_metadata_sync(query, max_results=max_results)
        else:
            # Return full paper objects
            papers = search_papers_sync(query, max_results=max_results)
            results = [
                {
                    "arxiv_id": paper.metadata.arxiv_id,
                    "title": paper.metadata.title,
                    "authors": [{"name": a.name, "affiliation": a.affiliation} for a in paper.metadata.authors],
                    "abstract": paper.metadata.abstract,
                    "pdf_url": str(paper.pdf_url),
                    "arxiv_url": str(paper.arxiv_url),
                    "relevance_score": paper.relevance_score,
                    "published_date": paper.metadata.published_date.isoformat() if paper.metadata.published_date else None,
                    "categories": paper.metadata.categories
                }
                for paper in papers
            ]
        
        return jsonify({
            "query": query,
            "count": len(results),
            "papers": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "pasa-research-fetcher"})

if __name__ == '__main__':
    app.run(debug=True)

# Usage:
# curl "http://localhost:5000/api/search?q=neural%20networks&max=5"
# curl "http://localhost:5000/api/search?q=computer%20vision&format=metadata&max=10"
```

### Academic Dashboard

```python
import streamlit as st
import pandas as pd
from pasa_research_fetcher import search_papers_sync
import plotly.express as px

st.title("Academic Research Dashboard")

# Sidebar controls
st.sidebar.header("Search Parameters")
query = st.sidebar.text_input("Research Query", "machine learning")
max_results = st.sidebar.slider("Max Results", 10, 100, 30)
search_button = st.sidebar.button("Search Papers")

if search_button and query:
    with st.spinner("Searching for papers..."):
        papers = search_papers_sync(query, max_results=max_results)
    
    if papers:
        st.success(f"Found {len(papers)} papers")
        
        # Convert to DataFrame for analysis
        data = []
        for paper in papers:
            data.append({
                "Title": paper.metadata.title,
                "Authors": ", ".join([a.name for a in paper.metadata.authors[:3]]),  # First 3 authors
                "Year": paper.metadata.published_date.year if paper.metadata.published_date else None,
                "Relevance": paper.relevance_score,
                "Categories": ", ".join(paper.metadata.categories[:2]),  # First 2 categories
                "ArXiv": paper.metadata.arxiv_id,
                "PDF": str(paper.pdf_url)
            })
        
        df = pd.DataFrame(data)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Papers", len(papers))
        with col2:
            avg_score = df["Relevance"].mean()
            st.metric("Avg Relevance", f"{avg_score:.3f}")
        with col3:
            year_range = df["Year"].max() - df["Year"].min() if df["Year"].notna().any() else 0
            st.metric("Year Range", f"{year_range} years")
        with col4:
            unique_categories = set()
            for cats in df["Categories"]:
                if pd.notna(cats):
                    unique_categories.update(cats.split(", "))
            st.metric("Categories", len(unique_categories))
        
        # Relevance score distribution
        st.subheader("Relevance Score Distribution")
        fig_hist = px.histogram(df, x="Relevance", bins=20, title="Distribution of Relevance Scores")
        st.plotly_chart(fig_hist)
        
        # Papers by year
        if df["Year"].notna().any():
            st.subheader("Papers by Year")
            year_counts = df["Year"].value_counts().sort_index()
            fig_year = px.bar(x=year_counts.index, y=year_counts.values, title="Number of Papers by Year")
            st.plotly_chart(fig_year)
        
        # Papers table
        st.subheader("Search Results")
        
        # Make titles clickable links to ArXiv
        df_display = df.copy()
        df_display["Title"] = df_display.apply(
            lambda row: f"[{row['Title'][:80]}...]({row['PDF']})" if len(row['Title']) > 80 else f"[{row['Title']}]({row['PDF']})",
            axis=1
        )
        
        st.dataframe(
            df_display[["Title", "Authors", "Year", "Relevance", "Categories"]],
            use_container_width=True
        )
        
        # Download options
        st.subheader("Export Data")
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name=f"research_papers_{query.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    
    else:
        st.warning("No papers found for your query. Try different search terms.")

# Run with: streamlit run academic_dashboard.py
```

## Batch Processing Examples

### Process Multiple Queries

```python
import asyncio
from pasa_research_fetcher import search_papers
import json

async def batch_search(queries: list, max_results_per_query: int = 20):
    """Search multiple queries in parallel"""
    
    # Create tasks for all queries
    tasks = [
        search_papers(query, max_results=max_results_per_query)
        for query in queries
    ]
    
    # Execute all searches concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    processed_results = {}
    for query, result in zip(queries, results):
        if isinstance(result, Exception):
            print(f"Error searching '{query}': {result}")
            processed_results[query] = []
        else:
            processed_results[query] = [
                {
                    "title": paper.metadata.title,
                    "authors": [a.name for a in paper.metadata.authors],
                    "arxiv_id": paper.metadata.arxiv_id,
                    "relevance_score": paper.relevance_score,
                    "pdf_url": str(paper.pdf_url)
                }
                for paper in result
            ]
    
    return processed_results

# Usage
async def main():
    research_topics = [
        "transformer neural networks",
        "computer vision object detection",
        "natural language processing BERT",
        "reinforcement learning deep Q-learning",
        "generative adversarial networks GAN"
    ]
    
    results = await batch_search(research_topics, max_results_per_query=15)
    
    # Save to file
    with open("batch_research_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    for topic, papers in results.items():
        print(f"{topic}: {len(papers)} papers")

asyncio.run(main())
```

### Literature Survey Builder

```python
import asyncio
from pasa_research_fetcher import search_papers
from datetime import datetime, timedelta
import csv

class LiteratureSurveyBuilder:
    def __init__(self):
        self.papers = []
        self.seen_arxiv_ids = set()
    
    async def add_topic(self, topic: str, max_papers: int = 50):
        """Add papers from a topic to the survey"""
        print(f"Searching for: {topic}")
        papers = await search_papers(topic, max_results=max_papers)
        
        # Deduplicate by ArXiv ID
        new_papers = [
            paper for paper in papers 
            if paper.metadata.arxiv_id not in self.seen_arxiv_ids
        ]
        
        self.papers.extend(new_papers)
        self.seen_arxiv_ids.update(paper.metadata.arxiv_id for paper in new_papers)
        
        print(f"Added {len(new_papers)} new papers (total: {len(self.papers)})")
        return new_papers
    
    async def build_comprehensive_survey(self, main_topic: str, related_topics: list):
        """Build a comprehensive literature survey"""
        
        # Start with main topic (more papers)
        await self.add_topic(main_topic, max_papers=100)
        
        # Add related topics
        for topic in related_topics:
            await self.add_topic(topic, max_papers=30)
        
        # Sort by relevance score
        self.papers.sort(key=lambda p: p.relevance_score, reverse=True)
        
        return self.papers
    
    def filter_by_date(self, years_back: int = 5):
        """Filter papers to recent years only"""
        cutoff_date = datetime.now() - timedelta(days=365 * years_back)
        
        filtered_papers = [
            paper for paper in self.papers
            if paper.metadata.published_date and paper.metadata.published_date >= cutoff_date
        ]
        
        print(f"Filtered to {len(filtered_papers)} papers from last {years_back} years")
        return filtered_papers
    
    def export_to_csv(self, filename: str):
        """Export survey to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'ArXiv ID', 'Title', 'Authors', 'Year', 'Categories',
                'Relevance Score', 'Abstract', 'PDF URL', 'ArXiv URL'
            ])
            
            for paper in self.papers:
                writer.writerow([
                    paper.metadata.arxiv_id,
                    paper.metadata.title,
                    '; '.join([a.name for a in paper.metadata.authors]),
                    paper.metadata.published_date.year if paper.metadata.published_date else 'Unknown',
                    '; '.join(paper.metadata.categories),
                    paper.relevance_score,
                    paper.metadata.abstract,
                    str(paper.pdf_url),
                    str(paper.arxiv_url)
                ])
        
        print(f"Exported {len(self.papers)} papers to {filename}")

# Usage
async def build_ml_survey():
    survey = LiteratureSurveyBuilder()
    
    # Build comprehensive survey on machine learning
    papers = await survey.build_comprehensive_survey(
        main_topic="machine learning deep neural networks",
        related_topics=[
            "convolutional neural networks CNN",
            "recurrent neural networks RNN LSTM",
            "transformer attention mechanism",
            "generative adversarial networks",
            "reinforcement learning policy gradient",
            "unsupervised learning representation learning",
            "transfer learning fine-tuning"
        ]
    )
    
    print(f"Total papers found: {len(papers)}")
    
    # Filter to recent papers
    recent_papers = survey.filter_by_date(years_back=3)
    
    # Export results
    survey.export_to_csv("ml_literature_survey_2021_2024.csv")
    
    # Print top papers
    print("\nTop 10 Most Relevant Papers:")
    for i, paper in enumerate(papers[:10], 1):
        print(f"{i}. {paper.metadata.title} (Score: {paper.relevance_score:.3f})")

asyncio.run(build_ml_survey())
```

## Command Line Examples

### Basic CLI Usage

```bash
# Simple search
pasa-fetcher search "attention mechanism transformers"

# Limit results
pasa-fetcher search "computer vision" --max 10

# Table format for readability
pasa-fetcher search "neural networks" --format table --max 15

# Download PDFs
pasa-fetcher search "deep learning" --pdfs --output ./papers --max 5

# Custom timeout for complex queries
pasa-fetcher search "multimodal machine learning vision language" --timeout 60000
```

### Shell Scripting

```bash
#!/bin/bash

# Research paper collection script
TOPICS=("machine learning" "computer vision" "natural language processing" "robotics")
OUTPUT_DIR="research_papers_$(date +%Y%m%d)"

mkdir -p "$OUTPUT_DIR"

for topic in "${TOPICS[@]}"; do
    echo "Collecting papers for: $topic"
    
    # Create topic directory
    topic_dir="$OUTPUT_DIR/${topic// /_}"
    mkdir -p "$topic_dir"
    
    # Search and download
    pasa-fetcher search "$topic optimization" \
        --pdfs \
        --output "$topic_dir" \
        --max 20 \
        --format json > "$topic_dir/papers.json"
    
    echo "Saved papers for $topic to $topic_dir"
done

echo "Collection complete! Check $OUTPUT_DIR directory"
```

These examples demonstrate the flexibility and power of the PASA Research Fetcher for various research workflows, from simple searches to complex academic applications.