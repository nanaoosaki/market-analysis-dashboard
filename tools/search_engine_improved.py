#!/usr/bin/env python3

import sys
import argparse
import logging
import time
import traceback
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class ImprovedDDGSearcher:
    BASE_URL = "https://html.duckduckgo.com/html/"
    
    def __init__(self, max_retries: int = 3, delay: int = 5, backoff_factor: float = 1.5):
        self.max_retries = max_retries
        self.initial_delay = delay
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://duckduckgo.com/',
            'Origin': 'https://duckduckgo.com',
            'Connection': 'keep-alive',
        })

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Perform a search with retry logic and error handling.
        """
        delay = self.initial_delay
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Search attempt {attempt + 1}/{self.max_retries} for query: {query}")
                
                # Use form data instead of URL parameters
                data = {
                    'q': query,
                    's': '0',
                    'dc': '1',
                    'o': 'json',
                    'api': '/d.js',
                }
                
                response = self.session.post(
                    self.BASE_URL,
                    data=data,
                    timeout=10
                )
                
                # Debug response
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {response.headers}")
                
                if response.status_code == 200:
                    # Save HTML for debugging if needed
                    with open('debug_response.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    results = self._parse_results(response.text, max_results)
                    if results:
                        logger.info(f"Successfully found {len(results)} results")
                        return results
                    else:
                        logger.warning("No results found in response")
                        # Debug HTML structure
                        soup = BeautifulSoup(response.text, 'html.parser')
                        logger.debug(f"Page title: {soup.title}")
                        logger.debug(f"Available classes: {[c.get('class', []) for c in soup.find_all(class_=True)]}")
                else:
                    logger.warning(f"Received status code: {response.status_code}")
                
            except requests.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= self.backoff_factor
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                traceback.print_exc(file=sys.stderr)
            
            if attempt < self.max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= self.backoff_factor
            else:
                logger.error("All retry attempts failed")
                break

        return []

    def _parse_results(self, html_content: str, max_results: int) -> List[Dict[str, str]]:
        """
        Parse the HTML content and extract search results.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Try different possible selectors
        result_elements = (
            soup.select('.result__body') or  # New layout
            soup.select('.results_links_deep') or  # Alternative layout
            soup.select('.result') or  # Classic layout
            soup.select('.web-result')  # Another possible layout
        )
        
        logger.info(f"Found {len(result_elements)} raw results")
        
        for result in result_elements[:max_results]:
            try:
                # Try multiple possible selectors for each element
                title_elem = (
                    result.select_one('.result__title a') or
                    result.select_one('.result__a') or
                    result.select_one('a')
                )
                
                snippet_elem = (
                    result.select_one('.result__snippet') or
                    result.select_one('.result__description') or
                    result.select_one('.result-snippet')
                )
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    if url and title:
                        results.append({
                            'url': url,
                            'title': title,
                            'snippet': snippet
                        })
                        logger.debug(f"Parsed result: {title}")
            
            except Exception as e:
                logger.error(f"Error parsing result: {str(e)}")
                continue
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Enhanced DuckDuckGo Search Tool')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--max-results', type=int, default=10,
                      help='Maximum number of results (default: 10)')
    parser.add_argument('--max-retries', type=int, default=3,
                      help='Maximum number of retry attempts (default: 3)')
    parser.add_argument('--delay', type=int, default=5,
                      help='Initial delay between retries in seconds (default: 5)')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    searcher = ImprovedDDGSearcher(
        max_retries=args.max_retries,
        delay=args.delay
    )
    
    results = searcher.search(args.query, args.max_results)
    
    if not results:
        logger.warning("No results found or search failed")
        return
    
    # Print results in a formatted way
    for i, result in enumerate(results, 1):
        print(f"\n=== Result {i} ===")
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Snippet: {result['snippet']}")

if __name__ == "__main__":
    main() 