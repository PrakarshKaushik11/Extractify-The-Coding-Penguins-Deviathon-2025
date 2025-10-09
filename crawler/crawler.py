import argparse
import requests
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from collections import deque
import json
import time
import os
from crawler.utils import get_robots_parser, is_allowed_by_robots, extract_main_text, normalize_url, get_canonical_url

def crawl(domain, max_depth, output_path):
    domain_parsed = urlparse(domain)
    base_domain = domain_parsed.netloc

    robots_parser = get_robots_parser(domain)
    visited = set()
    queue = deque([(domain, 0)])
    results = []

    while queue:
        url, depth = queue.popleft()
        if depth > max_depth:
            continue

        normalized_url = normalize_url(url)
        if normalized_url in visited:
            continue
        visited.add(normalized_url)

        # Check robots.txt permission
        if not is_allowed_by_robots(robots_parser, normalized_url):
            continue

        try:
            response = requests.get(normalized_url, timeout=10)
            if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                continue

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Follow canonical URL & avoid duplicates
            canonical_url = get_canonical_url(soup)
            if canonical_url:
                canonical_url = normalize_url(urljoin(normalized_url, canonical_url))
                if canonical_url != normalized_url and canonical_url in visited:
                    continue
                visited.add(canonical_url)
                url_to_store = canonical_url
            else:
                url_to_store = normalized_url

            # Extract main content text
            text = extract_main_text(soup)

            page_data = {
                "url": url_to_store,
                "title": soup.title.string.strip() if soup.title else "",
                "text": text,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "success"
            }
            results.append(page_data)
            print(f"Crawled: {url_to_store} (depth {depth})")

            # Extract same-domain links for further crawling
            if depth < max_depth:
                for link_tag in soup.find_all('a', href=True):
                    link = urljoin(url_to_store, link_tag['href'])
                    parsed_link = urlparse(link)

                    # Normalize and check domain constraint
                    normalized_link = normalize_url(link)
                    if parsed_link.netloc == base_domain and normalized_link not in visited:
                        queue.append((normalized_link, depth + 1))

        except Exception as e:
            print(f"Failed to crawl {url}: {e}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write results to JSONL
    with open(output_path, "w", encoding="utf-8") as f:
        for page in results:
            f.write(json.dumps(page, ensure_ascii=False) + "\n")
    print(f"Crawl finished. Saved {len(results)} pages to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web crawler for The Coding Penguins")
    parser.add_argument("--domain", required=True, help="Domain URL to crawl")
    parser.add_argument("--max_depth", type=int, default=2, help="Maximum crawl depth")
    parser.add_argument("--output", default="data/pages.jsonl", help="Output JSONL file path")

    args = parser.parse_args()
    crawl(args.domain, args.max_depth, args.output)
