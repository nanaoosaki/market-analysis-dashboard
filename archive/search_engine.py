"""
⚠️ DEPRECATED: DO NOT USE ⚠️
This file is archived for reference only.
Please use tools/search_engine_improved.py instead.
"""

#!/usr/bin/env python3

import argparse
import sys
import traceback
import time
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException

def search(query, max_results=10, max_retries=3, delay=5):
    """
    Search using DuckDuckGo and return results with URLs and text snippets.
    Uses the HTML backend which has proven to be more reliable.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        max_retries (int): Maximum number of retry attempts
        delay (int): Delay in seconds between retries
    """
    for attempt in range(max_retries):
        try:
            print(f"DEBUG: Searching for query: {query} (attempt {attempt + 1}/{max_retries})", file=sys.stderr)
            
            with DDGS() as ddgs:
                print(f"DEBUG: DDGS instance created", file=sys.stderr)
                
                try:
                    results = []
                    for r in ddgs.text(
                        query,
                        max_results=max_results,
                        backend='html'
                    ):
                        results.append(r)
                        print(f"DEBUG: Found result: {r.get('title', 'N/A')}", file=sys.stderr)
                        
                except DuckDuckGoSearchException as e:
                    if "Ratelimit" in str(e) and attempt < max_retries - 1:
                        print(f"DEBUG: Rate limited. Waiting {delay} seconds before retry...", file=sys.stderr)
                        time.sleep(delay)
                        continue
                    raise
                
                if not results:
                    print("DEBUG: No results found", file=sys.stderr)
                    return
                
                print(f"DEBUG: Found {len(results)} results", file=sys.stderr)
                
                for i, r in enumerate(results, 1):
                    print(f"\n=== Result {i} ===")
                    print(f"URL: {r.get('link', r.get('href', 'N/A'))}")
                    print(f"Title: {r.get('title', 'N/A')}")
                    print(f"Snippet: {r.get('snippet', r.get('body', 'N/A'))}")
                
                return  # Success! Exit the retry loop
                
        except Exception as e:
            if attempt == max_retries - 1:  # Only exit on the last attempt
                print(f"ERROR: Search failed after {max_retries} attempts: {str(e)}", file=sys.stderr)
                print(f"ERROR type: {type(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                sys.exit(1)
            print(f"DEBUG: Attempt {attempt + 1} failed: {str(e)}", file=sys.stderr)
            time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description="Search using DuckDuckGo API")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=10,
                      help="Maximum number of results (default: 10)")
    
    args = parser.parse_args()
    search(args.query, args.max_results)

if __name__ == "__main__":
    main() 