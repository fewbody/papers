#!/usr/bin/env python3
import feedparser
import json
import time
import re
from datetime import datetime

# Define RSS feeds
FEEDS = [
    {"url": "http://feeds.aps.org/rss/tocsec/PRL-NuclearPhysics.xml", "name": "Physical Review Letter"},
    {"url": "http://feeds.aps.org/rss/recent/prc.xml", "name": "Physical Review C"},
    {"url": "https://rss.arxiv.org/rss/nucl-th", "name": "arXiv for Nuclear Theory"},
    {"url": "https://iopscience.iop.org/journal/rss/0954-3899", "name": "Journal of Physics G: Nuclear and Particle Physics"},
    {"url": "http://feeds.feedburner.com/edp_epja?format=xml", "name": "European Physical Journal A"},
    {"url": "https://rss.sciencedirect.com/publication/science/03702693", "name": "Physics Letters B"},
    {"url": "https://rss.sciencedirect.com/publication/science/03759474", "name": "Nuclear Physics A"},
    {"url": "http://link.springer.com/search.rss?facet-content-type=Article&facet-journal-id=601&channel-name=Few-Body%20Systems", "name": "Few-Body Systems"},
    {"url": "https://iopscience.iop.org/journal/rss/1674-1137", "name": "Chinese Physics C"},
]

def fetch_new_articles():
    """
    Fetch all articles from RSS feeds without handling publication dates.
    
    Returns:
        list: A list of dictionaries containing article details (title, link, authors, source, summary).
    """
    all_papers = []
    
    for feed in FEEDS:
        print(f"Processing: {feed['name']}")
        try:
            # Add a delay to avoid hitting rate limits
            time.sleep(2)
            
            # Parse the feed
            parsed_feed = feedparser.parse(feed["url"])
            
            for entry in parsed_feed.entries:
                # Extract author information
                authors = "Unknown"
                if hasattr(entry, 'authors'):
                    authors = ", ".join([author.get("name", "") for author in entry.authors])
                elif hasattr(entry, 'author'):
                    authors = entry.author
                
                # Extract summary
                summary = entry.get('summary', '')
                if not summary and hasattr(entry, 'description'):
                    summary = entry.description
                
                # Clean summary by removing HTML tags
                summary = re.sub('<[^<]+?>', '', summary)
                
                # Add paper to the list with only the required fields
                all_papers.append({
                    "title": entry.get('title', 'No Title Available'),
                    "link": entry.get('link', '#'),
                    "authors": authors,
                    "source": feed["name"],
                    "summary": summary
                })
        except Exception as e:
            print(f"Error processing {feed['name']}: {e}")
    
    # No sorting by publication date; return papers in fetched order
    return all_papers

def main():
    """
    Main function to fetch new articles, compare with existing ones, and update the data file.
    """
    # Load existing data from data.json if it exists, excluding publicationDate
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Reconstruct existing papers with only desired fields
            existing_papers = [
                {
                    "title": paper.get("title", "No Title Available"),
                    "link": paper.get("link", "#"),
                    "authors": paper.get("authors", "Unknown"),
                    "source": paper.get("source", ""),
                    "summary": paper.get("summary", "")
                }
                for paper in data.get("papers", [])
            ]
    except FileNotFoundError:
        data = {"lastUpdated": None, "papers": []}
        existing_papers = []

    # Fetch all articles from RSS feeds
    new_articles = fetch_new_articles()
    
    # Create a set of existing article links for comparison
    existing_links = set(paper["link"] for paper in existing_papers)
    
    # Filter out articles already in data.json
    new_papers = [article for article in new_articles if article["link"] not in existing_links]
    
    # Add new papers to the existing list
    existing_papers.extend(new_papers)
    
    # Update the data dictionary
    data["papers"] = existing_papers
    data["lastUpdated"] = datetime.now().isoformat()
    
    # Save to JSON file
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Added {len(new_papers)} new papers. Total papers in data.json: {len(existing_papers)}")

if __name__ == "__main__":
    main()
