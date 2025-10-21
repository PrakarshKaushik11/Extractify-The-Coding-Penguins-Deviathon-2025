# api/main.py
from __future__ import annotations

import json
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# local modules
from crawler.scraper import crawl_domain
from extractor.nlp_pipeline import extract_entities

# Import validators
try:
    from api.validators import (
        validate_url,
        validate_keywords,
        validate_max_pages,
        validate_max_depth,
        validate_min_score,
        ValidationError
    )
except ImportError:
    # Fallback if validators module is not available
    ValidationError = ValueError
    def validate_url(url): return url
    def validate_keywords(kw): return kw
    def validate_max_pages(p): return p
    def validate_max_depth(d): return d
    def validate_min_score(s): return s

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
    
    @field_validator('domain')
    @classmethod
    def validate_domain_field(cls, v):
        """Validate URL format."""
        try:
            return validate_url(v)
        except ValidationError as e:
            raise ValueError(str(e))
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords_field(cls, v):
        """Validate and sanitize keywords."""
        if v is None:
            return []
        try:
            return validate_keywords(v)
        except ValidationError as e:
            raise ValueError(str(e))
    
    @field_validator('max_pages')
    @classmethod
    def validate_max_pages_field(cls, v):
        """Validate max_pages range."""
        try:
            return validate_max_pages(v)
        except ValidationError as e:
            raise ValueError(str(e))
    
    @field_validator('max_depth')
    @classmethod
    def validate_max_depth_field(cls, v):
        """Validate max_depth range."""
        try:
            return validate_max_depth(v)
        except ValidationError as e:
            raise ValueError(str(e))


class ExtractRequest(BaseModel):
    keywords: Optional[List[str]] = []
    target: Optional[str] = "auto"
    min_score: Optional[float] = 0.0  # kept for UI compatibility but not forwarded if extractor doesn't accept it
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords_field(cls, v):
        """Validate and sanitize keywords."""
        if v is None:
            return []
        try:
            return validate_keywords(v)
        except ValidationError as e:
            raise ValueError(str(e))
    
    @field_validator('min_score')
    @classmethod
    def validate_min_score_field(cls, v):
        """Validate min_score range."""
        if v is None:
            return 0.0
        try:
            return validate_min_score(v)
        except ValidationError as e:
            raise ValueError(str(e))


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
    # Clear previous crawl and extraction data
    try:
        for path in [PAGES_PATH, ENTITIES_PATH]:
            try:
                path.write_text("", encoding="utf-8")
            except Exception:
                pass
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
    LOG.info("Received extract request: target=%s keywords=%s min_score=%s", payload.target, payload.keywords, payload.min_score)
    if not PAGES_PATH.exists():
        raise HTTPException(status_code=400, detail="No pages found. Run /api/crawl or /crawl first.")
    try:
        # NOTE: extractor.extract_entities historically has different signatures depending on implementation.
        # To remain compatible we only pass the stable, core args. If your extractor supports min_score, update here.
        out = extract_entities(
            pages_path=str(PAGES_PATH),
            entities_path=str(ENTITIES_PATH),
            keywords=payload.keywords or [],
            target=payload.target or "auto",
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
    # Clear previous crawl and extraction data
    try:
        for path in [PAGES_PATH, ENTITIES_PATH]:
            try:
                path.write_text("", encoding="utf-8")
            except Exception:
                pass
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
@app.get("/", include_in_schema=False)
def root() -> HTMLResponse:
        """Simple landing page to avoid 404 at service root."""
        html = (
                """
                <!doctype html>
                <html lang="en">
                <head>
                    <meta charset="utf-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1" />
                    <title>Extractify API</title>
                    <style>
                        body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;line-height:1.5;padding:2rem;max-width:720px;margin:auto}
                        code{background:#f4f4f5;padding:.2rem .4rem;border-radius:.25rem}
                        a{color:#2563eb;text-decoration:none}
                        a:hover{text-decoration:underline}
                    </style>
                </head>
                <body>
                    <h1>Extractify — Backend API</h1>
                    <p>Welcome! This is the backend service. Useful links:</p>
                    <ul>
                        <li><a href="/docs">Swagger UI</a> (<code>/docs</code>)</li>
                        <li><a href="/api/health">Health</a> (<code>/api/health</code>)</li>
                        <li>Results: <code>/api/results</code></li>
                        <li>Crawl+Extract: <code>POST /api/crawl-and-extract</code></li>
                    </ul>
                </body>
                </html>
                """
        )
        return HTMLResponse(content=html)

@app.get("/api", include_in_schema=False)
def api_root() -> RedirectResponse:
        """Redirect bare /api to the interactive docs for convenience."""
        return RedirectResponse(url="/docs")
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
def api_crawl_and_extract(payload: CrawlRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Start crawl-and-extract as a background task and return immediately."""
    LOG.info("crawl-and-extract request received: %s", payload.domain)
    
    # Clear previous data immediately
    try:
        for path in [PAGES_PATH, ENTITIES_PATH]:
            try:
                path.write_text("", encoding="utf-8")
            except Exception:
                pass
    except Exception as e:
        LOG.warning("Failed to clear data files: %s", e)
    
    # Run crawl-and-extract in background
    background_tasks.add_task(_do_crawl_and_extract, payload)
    
    return {
        "status": "started",
        "message": "Crawl and extraction started in background",
        "domain": payload.domain,
        "max_pages": payload.max_pages,
        "max_depth": payload.max_depth
    }


@app.post("/crawl-and-extract")
def crawl_and_extract(payload: CrawlRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    return api_crawl_and_extract(payload, background_tasks)
