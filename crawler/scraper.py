# crawler/scraper.py
from __future__ import annotations

import re
import urllib.parse
from collections import deque
from dataclasses import dataclass
from typing import Set, List, Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}
FETCH_TIMEOUT = 15

@dataclass
class Page:
    url: str
    text: str

@dataclass
class CrawlResult:
    pages: List[Page]
    visited: List[str]

def _same_domain(base: str, link: str) -> bool:
    try:
        b = urllib.parse.urlparse(base)
        l = urllib.parse.urlparse(link)
        return (b.scheme, b.netloc) == (l.scheme, l.netloc)
    except Exception:
        return False

def _abs_url(base: str, href: str) -> Optional[str]:
    if not href:
        return None
    try:
        url = urllib.parse.urljoin(base, href)
        u = urllib.parse.urlparse(url)
        if u.scheme not in ("http", "https"):
            return None
        return urllib.parse.urlunparse((u.scheme, u.netloc, u.path, "", u.query, ""))
    except Exception:
        return None

NON_VISIBLE = {"script","style","noscript","footer","header","nav"}

def extract_clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(NON_VISIBLE):
        t.decompose()
    chunks = []
    for el in soup.find_all(["h1","h2","h3","h4","h5","p","li","span","div","a"]):
        txt = el.get_text(" ", strip=True)
        if not txt:
            continue
        if len(txt) < 2:
            continue
        if txt.lower() in ("home","read more","learn more","menu"):
            continue
        chunks.append(txt)
    text = " ".join(chunks)
    return re.sub(r"\s+", " ", text).strip()

ALUMNI_HINT_LINK = ("alumni","convocation","placement","career","graduates","success")

def crawl_domain(start_url: str, max_pages: int = 150, max_depth: int = 2) -> CrawlResult:
    """Focused crawler that biases alumni-like links. Returns Page(text,url)."""
    visited: Set[str] = set()
    pages: List[Page] = []

    start = urllib.parse.urlparse(start_url)
    base = f"{start.scheme}://{start.netloc}"

    frontier: deque = deque()
    frontier.append((start_url, 0))

    while frontier and len(pages) < max_pages:
        url, depth = frontier.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            r = requests.get(url, headers=HEADERS, timeout=FETCH_TIMEOUT)
            r.raise_for_status()
            ctype = r.headers.get("Content-Type","")
            if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
                continue
            html = r.text
        except Exception:
            continue

        text = extract_clean_text(html)
        pages.append(Page(url=url, text=text))

        if depth >= max_depth:
            continue

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            u = _abs_url(url, a.get("href"))
            if not u:
                continue
            if not _same_domain(base, u):
                continue
            if u in visited:
                continue
            hl = u.lower()
            if any(s in hl for s in ALUMNI_HINT_LINK):
                frontier.appendleft((u, depth + 1))
            else:
                frontier.append((u, depth + 1))

    return CrawlResult(pages=pages, visited=list(visited))

__all__ = ["crawl_domain", "extract_clean_text", "Page", "CrawlResult"]