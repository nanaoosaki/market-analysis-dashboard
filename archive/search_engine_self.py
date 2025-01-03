"""
⚠️ DEPRECATED: DO NOT USE ⚠️
This file is archived for reference only.
Please use tools/search_engine_improved.py instead.
"""

import requests
from bs4 import BeautifulSoup
import sys
import argparse
from typing import List, Dict
import logging
import time
from duckduckgo_search import DDGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DuckDuckGoScraper:
    BASE_URL = "https://html.duckduckgo.com/html/"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        with DDGS() as ddgs:
            try:
                return list(ddgs.text(query, max_results=max_results, backend='html'))
            except requests.RequestException as e:
                logger.error(f"Error performing search: {str(e)}")
                return []

def main():
    parser = argparse.ArgumentParser(description='Search DuckDuckGo and return results')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results to return')
    
    args = parser.parse_args()
    
    scraper = DuckDuckGoScraper()
    results = scraper.search(args.query, args.max_results)
    
    # Print results in a formatted way
    for result in results:
        print(f"\nURL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Snippet: {result['snippet']}")

if __name__ == "__main__":
    main()
