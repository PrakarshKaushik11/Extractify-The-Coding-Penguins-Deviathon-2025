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


# -----------------------
# Routes
# -----------------------
@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "app": "Extractify — Entity Extractor",
        "ignore_robots": (os.getenv("CP_IGNORE_ROBOTS", "0") == "1"),
        "pages_file_present": PAGES_PATH.exists(),
        "entities_file_present": ENTITIES_PATH.exists(),
    }


@app.post("/api/crawl")
def crawl(payload: CrawlRequest) -> Dict[str, Any]:
    """
    Crawl a domain and write data/pages.jsonl.
    Returns a small summary with sample URLs and stats.
    """
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract")
def extract(payload: ExtractRequest) -> Dict[str, Any]:
    """
    Run the extractor over data/pages.jsonl and write data/entities.json.
    Returns entities summary in the response.
    """
    LOG.info("Received extract request: target=%s keywords=%s", payload.target, payload.keywords)
    if not PAGES_PATH.exists():
        raise HTTPException(status_code=400, detail="No pages found. Run /api/crawl first.")
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
        raise HTTPException(status_code=500, detail=f"Extractor error: {e}")


@app.get("/api/results")
def results() -> List[Dict[str, Any]]:
    """
    Read the last saved entities from data/entities.json.
    Returns [] if missing or invalid.
    """
    data = _read_json(ENTITIES_PATH)
    if data is None:
        return []
    if isinstance(data, dict) and "entities" in data:
        return data["entities"]
    if isinstance(data, list):
        return data
    return []


@app.post("/api/crawl-and-extract")
def crawl_and_extract(payload: CrawlRequest) -> Dict[str, Any]:
    """
    Convenience endpoint used by the UI button: crawls then extracts.
    Runs crawl_domain and extract_entities sequentially and returns both summaries.
    """
    LOG.info("crawl-and-extract start: %s", payload.domain)
    try:
        crawl_result = crawl_domain(
            domain=payload.domain,
            keywords=payload.keywords or [],
            max_pages=payload.max_pages,
            max_depth=payload.max_depth,
            out_path=str(PAGES_PATH),
        )
    except Exception as e:
        LOG.exception("crawl part failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Crawl error: {e}")

    try:
        extract_result = extract_entities(
            pages_path=str(PAGES_PATH),
            entities_path=str(ENTITIES_PATH),
            keywords=payload.keywords or [],
            target="auto",
        )
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

    LOG.info("crawl-and-extract done: pages=%s entities=%s", crawl_result.get("pages_scanned"), 
             (len(extract_result.get("entities")) if isinstance(extract_result, dict) and "entities" in extract_result else "n/a"))

    return {"crawl": crawl_result, "extract": extract_result}
