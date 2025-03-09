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
    Fetch all articles from RSS feeds.
    
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
    
    return all_papers

def main():
    """
    Main function to fetch new articles, compare with existing ones, and update the data files.
    - source.json: Contains all historical articles
    - data.json: Contains only the newest batch of articles from current run
    """
    # Load existing data from source.json if it exists
    try:
        with open('source.json', 'r', encoding='utf-8') as f:
            source_data = json.load(f)
            existing_papers = source_data.get("papers", [])
    except FileNotFoundError:
        source_data = {"lastUpdated": None, "papers": []}
        existing_papers = []

    # Fetch all articles from RSS feeds
    all_articles = fetch_new_articles()
    
    # Create a set of existing article links for comparison
    existing_links = set(paper["link"] for paper in existing_papers)
    
    # Filter to get only new articles
    new_papers = [article for article in all_articles if article["link"] not in existing_links]
    
    # Update source.json with all papers (existing + new)
    source_data["papers"] = existing_papers + new_papers
    source_data["lastUpdated"] = datetime.now().isoformat()
    
    with open('source.json', 'w', encoding='utf-8') as f:
        json.dump(source_data, f, ensure_ascii=False, indent=2)
    
    # Create data.json with only the new papers from this run
    data_json = {
        "lastUpdated": datetime.now().isoformat(),
        "papers": new_papers
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data_json, f, ensure_ascii=False, indent=2)
    
    print(f"Found {len(new_papers)} new papers in this run.")
    print(f"Total papers in source.json: {len(source_data['papers'])}")
    print(f"New papers added to data.json: {len(new_papers)}")

if __name__ == "__main__":
    main()
