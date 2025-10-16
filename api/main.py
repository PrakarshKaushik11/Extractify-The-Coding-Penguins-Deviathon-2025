# api/main.py
from __future__ import annotations

import json
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# local modules
from crawler.scraper import crawl_domain
from extractor.nlp_pipeline import extract_entities

# -----------------------
# Logging
# -----------------------
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("extractify.api")

# -----------------------
# Paths / Data
# -----------------------
# Keep data directory relative to the repository working directory.
DATA_DIR = Path("data")
PAGES_PATH = DATA_DIR / "pages.jsonl"
ENTITIES_PATH = DATA_DIR / "entities.json"

# -----------------------
# FastAPI app + CORS
# -----------------------
app = FastAPI(
    title="Extractify — The Coding Penguins Project (Deviathon 2025)",
    version="1.0.0"
)

# Allow all origins for now (use specific origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Pydantic models
# -----------------------
class CrawlRequest(BaseModel):
    domain: str
    keywords: Optional[List[str]] = []
    max_pages: int = 20
    max_depth: int = 2


class ExtractRequest(BaseModel):
    keywords: Optional[List[str]] = []
    target: Optional[str] = "auto"
    min_score: Optional[float] = 0.0


# -----------------------
# Helper functions
# -----------------------
def _read_json(path: Path) -> Any:
    """Safely read a JSON file. Returns None if file missing."""
    try:
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        return json.loads(text)
    except json.JSONDecodeError:
        LOG.warning("JSON decode error reading %s — returning empty list", path)
        return []
    except Exception as e:
        LOG.exception("Unexpected error reading %s: %s", path, e)
        return []


def _write_json(path: Path, payload: Any) -> None:
    """Atomically write JSON to path (creates parent directories)."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        LOG.exception("Failed to write JSON to %s", path)
        raise


# Implementation helpers so we can expose both /api/* and top-level endpoints
def _do_crawl(payload: CrawlRequest) -> Dict[str, Any]:
    LOG.info("Received crawl request: domain=%s pages=%s depth=%s", payload.domain, payload.max_pages, payload.max_depth)
    try:
        result = crawl_domain(
            domain=payload.domain,
            keywords=payload.keywords or [],
            max_pages=payload.max_pages,
            max_depth=payload.max_depth,
            out_path=str(PAGES_PATH),
        )
        LOG.info("Crawl finished: %s", result)
        return result
    except Exception as e:
        LOG.exception("Crawl failed for domain %s: %s", payload.domain, e)
        raise


def _do_extract(payload: ExtractRequest) -> Any:
    LOG.info("Received extract request: target=%s keywords=%s", payload.target, payload.keywords)
    if not PAGES_PATH.exists():
        raise HTTPException(status_code=400, detail="No pages found. Run /api/crawl or /crawl first.")
    try:
        out = extract_entities(
            pages_path=str(PAGES_PATH),
            entities_path=str(ENTITIES_PATH),
            keywords=payload.keywords or [],
            target=payload.target or "auto",
            min_score=payload.min_score or 0.0,
        )
        # write output if extractor returned a serializable result
        try:
            if isinstance(out, dict) and "entities" in out:
                _write_json(ENTITIES_PATH, out)
            elif isinstance(out, list):
                _write_json(ENTITIES_PATH, out)
        except Exception:
            LOG.warning("Could not persist extraction output to %s", ENTITIES_PATH)
        return out
    except HTTPException:
        # re-raise HTTP errors from extractor
        raise
    except Exception as e:
        LOG.exception("Extraction failed: %s", e)
        raise


def _do_results() -> List[Dict[str, Any]]:
    data = _read_json(ENTITIES_PATH)
    if data is None:
        return []
    if isinstance(data, dict) and "entities" in data:
        return data["entities"]
    if isinstance(data, list):
        return data
    return []


def _do_crawl_and_extract(payload: CrawlRequest) -> Dict[str, Any]:
    LOG.info("crawl-and-extract start: %s", payload.domain)
    try:
        crawl_result = _do_crawl(payload)
    except Exception as e:
        LOG.exception("crawl part failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Crawl error: {e}")

    try:
        extract_payload = ExtractRequest(keywords=payload.keywords or [], target="auto")
        extract_result = _do_extract(extract_payload)
    except Exception as e:
        LOG.exception("extract part failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Extract error: {e}")

    # persist entities if shape ok
    try:
        if isinstance(extract_result, dict) and "entities" in extract_result:
            _write_json(ENTITIES_PATH, extract_result)
        elif isinstance(extract_result, list):
            _write_json(ENTITIES_PATH, extract_result)
    except Exception:
        LOG.warning("Failed to persist entities.json after crawl-and-extract")

    LOG.info(
        "crawl-and-extract done: pages=%s entities=%s",
        crawl_result.get("pages_scanned"),
        (len(extract_result.get("entities")) if isinstance(extract_result, dict) and "entities" in extract_result else "n/a"),
    )

    return {"crawl": crawl_result, "extract": extract_result}


# -----------------------
# Routes (both /api/* and top-level duplicates)
# -----------------------
@app.get("/api/health")
def api_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "app": "Extractify — Entity Extractor",
        "ignore_robots": (os.getenv("CP_IGNORE_ROBOTS", "0") == "1"),
        "pages_file_present": PAGES_PATH.exists(),
        "entities_file_present": ENTITIES_PATH.exists(),
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    # duplicate top-level health for non-/api clients
    return api_health()


# Crawl
@app.post("/api/crawl")
def api_crawl(payload: CrawlRequest) -> Dict[str, Any]:
    try:
        return _do_crawl(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crawl")
def crawl(payload: CrawlRequest) -> Dict[str, Any]:
    return api_crawl(payload)


# Extract
@app.post("/api/extract")
def api_extract(payload: ExtractRequest) -> Dict[str, Any]:
    try:
        return _do_extract(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract")
def extract(payload: ExtractRequest) -> Dict[str, Any]:
    return api_extract(payload)


# Results
@app.get("/api/results")
def api_results() -> List[Dict[str, Any]]:
    return _do_results()


@app.get("/results")
def results() -> List[Dict[str, Any]]:
    return api_results()


# Crawl-and-extract convenience endpoint
@app.post("/api/crawl-and-extract")
def api_crawl_and_extract(payload: CrawlRequest) -> Dict[str, Any]:
    try:
        return _do_crawl_and_extract(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/crawl-and-extract")
def crawl_and_extract(payload: CrawlRequest) -> Dict[str, Any]:
    return api_crawl_and_extract(payload)
