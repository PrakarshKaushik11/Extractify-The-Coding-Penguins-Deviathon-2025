# crawler/scraper.py
from __future__ import annotations

import json
import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Iterable, Set, Dict, Any, List
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup


@dataclass
class Page:
    url: str
    title: str
    text: str


def _same_host(u: str, root: str) -> bool:
    pu, pr = urlparse(u), urlparse(root)
    return pu.netloc == pr.netloc


def _normalize(u: str) -> str:
    # drop fragments and normalize trailing slashes
    u, _ = urldefrag(u)
    if u.endswith("/index.html"):
        u = u[: -len("/index.html")]
    return u.rstrip("/")


def _extract_links(html: str, base_url: str) -> Set[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href").strip()
        if not href:
            continue
        if href.startswith("javascript:") or href.startswith("mailto:"):
            continue
        full = _normalize(urljoin(base_url, href))
        links.add(full)
    return links


def _clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # collapse whitespace
    return re.sub(r"\s+", " ", text)


def _fetch(session: requests.Session, url: str, timeout: int = 15) -> requests.Response | None:
    try:
        r = session.get(url, timeout=timeout, headers={"User-Agent": "TheCodingPenguinsBot/1.0"})
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            return r
        return None
    except requests.RequestException:
        return None


def crawl_domain(
    domain: str,
    keywords: List[str],
    max_pages: int,
    max_depth: int,
    out_path: str,
) -> Dict[str, Any]:
    """
    Breadth-first crawl restricted to the same host. Saves JSONL lines with:
    {"url": ..., "title": ..., "text": ...}
    """
    start = time.time()
    root = _normalize(domain)
    seen: Set[str] = set()
    q = deque([(root, 0)])
    pages: List[Page] = []

    session = requests.Session()

    while q and len(pages) < max_pages:
        url, depth = q.popleft()
        if url in seen:
            continue
        seen.add(url)

        resp = _fetch(session, url)
        if not resp:
            continue

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else ""
        text = _clean_text(html)

        pages.append(Page(url=url, title=title, text=text))

        if depth < max_depth:
            for link in _extract_links(html, url):
                if _same_host(link, root) and link not in seen:
                    q.append((link, depth + 1))

    # write JSONL
    out_lines = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for p in pages:
            f.write(json.dumps({"url": p.url, "title": p.title, "text": p.text}, ensure_ascii=False) + "\n")
            out_lines += 1

    elapsed = round(time.time() - start, 2)
    return {
        "domain": root,
        "pages_scanned": len(pages),
        "sample_urls": [p.url for p in pages[:5]],
        "elapsed": elapsed,
        "used_fallback": 0,
    }
