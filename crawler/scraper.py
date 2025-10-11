# crawler/scraper.py
from __future__ import annotations

import json
import re
import time
import logging
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Set, Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from urllib import robotparser

LOG = logging.getLogger("penguins.crawler")
LOG.setLevel(logging.INFO)

# Env toggles:
#   CP_IGNORE_ROBOTS=1    -> ignore robots.txt (not recommended except demos)
#   CP_REQUEST_DELAY_MS   -> delay between requests to same host (default 300ms)
#   CP_MAX_RETRIES        -> HTTP retries (default 2)
#   CP_TIMEOUT_SEC        -> per-request timeout (default 25)

def _should_ignore_robots() -> bool:
    import os
    return os.getenv("CP_IGNORE_ROBOTS", "0") == "1"

def _delay_ms() -> int:
    import os
    try: return int(os.getenv("CP_REQUEST_DELAY_MS", "300"))
    except: return 300

def _timeout_sec() -> int:
    import os
    try: return int(os.getenv("CP_TIMEOUT_SEC", "25"))
    except: return 25

def _max_retries() -> int:
    import os
    try: return int(os.getenv("CP_MAX_RETRIES", "2"))
    except: return 2

@dataclass
class Page:
    url: str
    title: Optional[str]
    text: str

def _normalize_url(base_url: str, link: str) -> Optional[str]:
    try:
        u = urljoin(base_url, link)
        u, _ = urldefrag(u)
        parsed = urlparse(u)
        if not parsed.scheme.startswith("http"):
            return None
        return parsed.geturl()
    except Exception:
        return None

def _same_site(u: str, root: str) -> bool:
    try:
        return urlparse(u).netloc.lower() == urlparse(root).netloc.lower()
    except Exception:
        return False

def _extract_links(base_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if not href: 
            continue
        if a.get("rel") and any(r.lower() == "nofollow" for r in a.get("rel")):
            # keep internal links even if nofollow? safer: allow; here we skip
            pass
        u = _normalize_url(base_url, href)
        if u: links.append(u)
    return links

def _clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # collapse whitespace
    return re.sub(r"\s+", " ", text)

def _session_with_retries() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=_max_retries(),
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

def _fetch(session: requests.Session, url: str, timeout: Optional[int] = None) -> Optional[requests.Response]:
    try:
        r = session.get(
            url,
            timeout=timeout or _timeout_sec(),
            headers={
                "User-Agent": "TheCodingPenguinsBot/1.1 (+https://localhost)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            return r
        return None
    except requests.RequestException:
        return None

def _robots_allowed(root: str, url: str) -> bool:
    if _should_ignore_robots():
        return True
    try:
        rp = robotparser.RobotFileParser()
        parsed = urlparse(root)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception:
        return True

def crawl_domain(
    domain: str,
    keywords: List[str],
    max_pages: int,
    max_depth: int,
    out_path: str,
) -> Dict[str, Any]:
    """
    BFS crawl inside a single domain. Writes JSONL lines: {"url","title","text"} to out_path.
    """
    start = time.time()
    root = domain.rstrip("/")
    seen: Set[str] = set()
    queue = deque([(root, 0)])
    pages: List[Page] = []

    session = _session_with_retries()
    delay = _delay_ms() / 1000.0

    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()
        if url in seen:
            continue
        seen.add(url)

        if depth > max_depth:
            continue
        if not _same_site(url, root):
            continue
        if not _robots_allowed(root, url):
            continue

        resp = _fetch(session, url)
        if not resp:
            continue

        html = resp.text
        title = None
        try:
            soup = BeautifulSoup(html, "html.parser")
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
        except Exception:
            pass

        text = _clean_text(html)
        pages.append(Page(url=url, title=title, text=text))

        # simple keyword gate to avoid queue blowup
        body_low = (title or "").lower() + " " + text[:4000].lower()
        kw_ok = True if not keywords else any(k.strip().lower() in body_low for k in keywords if k.strip())
        if kw_ok:
            for link in _extract_links(url, html):
                if link not in seen and _same_site(link, root):
                    queue.append((link, depth + 1))

        if delay > 0:
            time.sleep(delay)

        # soft stop if we are clearly not making progress
        if len(seen) > max_pages * 8:
            break

    # Write output
    out_lines = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for p in pages:
            f.write(json.dumps({"url": p.url, "title": p.title, "text": p.text}, ensure_ascii=False) + "\n")
            out_lines += 1

    elapsed = round(time.time() - start, 2)
    LOG.info("Crawl done: %s pages, elapsed=%ss -> %s", len(pages), elapsed, out_path)
    return {
        "domain": root,
        "pages_scanned": len(pages),
        "sample_urls": [p.url for p in pages[:5]],
        "elapsed": elapsed,
        "used_fallback": 0,
    }
