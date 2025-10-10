# api/main.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, AnyHttpUrl

from crawler.scraper import crawl_domain
from extractor.nlp_pipeline import extract_entities_from_texts

# Optional modules
_SEM_AVAILABLE = True
try:
    from extractor.semantic_ranker import SemanticRanker
    from extractor.type_filters import allow_entity
except Exception:
    _SEM_AVAILABLE = False

_AUTO_AVAILABLE = True
try:
    from extractor.keyphrase import top_keyphrases
    from extractor.auto_intent import infer_types
except Exception:
    _AUTO_AVAILABLE = False

APP_NAME = "The Coding Penguins — Entity Extractor"
IGNORE_ROBOTS = os.environ.get("CP_IGNORE_ROBOTS", "0") == "1"

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

class CrawlRequest(BaseModel):
    domain: AnyHttpUrl
    keywords: List[str] = Field(default_factory=list)
    max_pages: int = Field(150, ge=1, le=2000)
    max_depth: int = Field(2, ge=0, le=6)

class ExtractRequest(BaseModel):
    url: AnyHttpUrl
    keywords: List[str] = Field(default_factory=list)

class CrawlAndExtractRequest(BaseModel):
    domain: AnyHttpUrl
    keywords: List[str] = Field(default_factory=list)  # optional in auto
    max_pages: int = Field(150, ge=1, le=2000)
    max_depth: int = Field(2, ge=0, le=6)
    target_type: str = Field("auto", description="auto|person|alumni|judge|minister|tech_term|org|location|generic")
    semantic: bool = True

def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()
    return " ".join(t.strip() for t in soup.stripped_strings)

def _fetch_single_page(url: str, timeout: int = 15) -> Dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    ctype = r.headers.get("Content-Type", "")
    if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
        raise HTTPException(status_code=400, detail=f"URL does not look like HTML (Content-Type: {ctype})")
    text = _extract_text_from_html(r.text)
    return {"url": url, "text": text}

def _apply_semantic_rerank(texts: List[Dict[str,str]], terms: List[str], type_hint: str, top_k: int = 120):
    if not _SEM_AVAILABLE:
        return texts, None, False
    try:
        ranker = SemanticRanker()
        ranked = ranker.rank(texts, query_terms=terms, require_alumni=(type_hint == "alumni"))
        if not ranked:
            return texts, None, False
        ranked_top = ranked[: min(top_k, len(ranked))]
        focused = [{"url": rc.url, "text": rc.text} for rc in ranked_top]
        return focused, ranked_top, True
    except Exception:
        return texts, None, False

def _join_semantic_score(entities: List[Dict[str, Any]], ranked_meta) -> None:
    if not ranked_meta:
        for e in entities:
            e["sem_score"] = 0.0
        return
    by_url: Dict[str, List[Any]] = {}
    for rc in ranked_meta:
        by_url.setdefault(rc.url, []).append(rc)
    for e in entities:
        url = e.get("context_url") or ""
        snippet = (e.get("snippet") or "")[:60]
        nm = (e.get("name") or "")[:40]
        e["sem_score"] = 0.0
        if not url or url not in by_url:
            continue
        best, best_sim = None, -1
        for rc in by_url[url]:
            sim = 0
            if snippet and snippet in rc.text: sim += 2
            if nm and nm in rc.text: sim += 1
            if sim > best_sim:
                best_sim, best = sim, rc
        if best is not None:
            e["sem_score"] = float(best.sem_score)

def _final_rescore_and_filter_multi(entities, types):
    if not entities:
        return []
    _allow = allow_entity if _SEM_AVAILABLE else (lambda e, _: True)
    kept = []
    for e in entities:
        if "generic" not in types:
            ok = any(_allow(e, t) for t in types)
            if not ok:
                continue
        base = float(e.get("score", 0.0))
        sem  = float(e.get("sem_score", 0.0))
        e["score"] = round(min(0.99, max(0.0, 0.45*sem + 0.55*base)), 3)
        kept.append(e)
    if not kept:
        return []
    scores = sorted(x["score"] for x in kept)
    cut = scores[int(0.75*(len(scores)-1))]
    kept = [x for x in kept if x["score"] >= cut or x["score"] >= 0.60]
    kept.sort(key=lambda x: x["score"], reverse=True)
    return kept

def _auto_terms_and_types(pages, user_terms: List[str], target_type: str):
    used_auto = False
    if target_type != "auto" and user_terms:
        return user_terms, [target_type], used_auto

    terms = user_terms[:]
    if _AUTO_AVAILABLE:
        texts = [p["text"] for p in pages[:12] if p.get("text")]
        mined = top_keyphrases(texts, k=12)
        seen, expanded = set(), []
        for t in (terms + mined):
            tl = t.strip().lower()
            if tl and tl not in seen:
                seen.add(tl); expanded.append(t.strip())
        terms = expanded[:20]
        types = infer_types(terms) or ["generic"]
        used_auto = True
    else:
        types = [target_type if target_type != "auto" else "person"]
    return terms, types, used_auto

@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "ignore_robots": IGNORE_ROBOTS,
        "semantic_available": _SEM_AVAILABLE,
        "auto_available": _AUTO_AVAILABLE,
    }

@app.post("/crawl")
def crawl(req: CrawlRequest):
    t0 = time.time()
    res = crawl_domain(str(req.domain), max_pages=req.max_pages, max_depth=req.max_depth)
    t1 = time.time()
    sample = list(res.visited)[:10]
    return {
        "domain": str(req.domain),
        "elapsed_sec": round(t1 - t0, 2),
        "pages_scanned": len(res.pages),
        "sample_urls": sample,
    }

@app.post("/extract")
def extract(req: ExtractRequest):
    try:
        page = _fetch_single_page(str(req.url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fetch error: {e}")
    try:
        entities = extract_entities_from_texts([page], req.keywords)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extractor error: {e}")
    return {"url": str(req.url), "entities": entities}

@app.post("/crawl-and-extract")
def crawl_and_extract(req: CrawlAndExtractRequest):
    t0 = time.time()
    result = crawl_domain(str(req.domain), max_pages=req.max_pages, max_depth=req.max_depth)
    pages = [{"url": p.url, "text": p.text} for p in result.pages]
    if not pages:
        return {
            "domain": str(req.domain),
            "pages_scanned": 0,
            "entities": [],
            "used_semantic": False,
            "target_type": req.target_type,
            "auto_types": [],
            "expanded_keywords": [],
        }

    terms, inferred_types, used_auto = _auto_terms_and_types(pages, req.keywords, req.target_type)

    type_hint = req.target_type if req.target_type != "auto" else ("alumni" if "alumni" in inferred_types else "person")
    focused_pages, ranked_meta, used_semantic = _apply_semantic_rerank(
        pages, terms, type_hint
    ) if req.semantic else (pages, None, False)

    try:
        entities = extract_entities_from_texts(focused_pages, terms)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extractor error: {e}")

    _join_semantic_score(entities, ranked_meta)
    entities = _final_rescore_and_filter_multi(entities, inferred_types)

    t1 = time.time()
    return {
        "domain": str(req.domain),
        "elapsed_sec": round(t1 - t0, 2),
        "pages_scanned": len(result.pages),
        "entities": entities,
        "used_semantic": bool(used_semantic),
        "target_type": req.target_type,
        "auto_types": inferred_types,
        "expanded_keywords": terms[:20],
        "used_auto": used_auto,
    }
