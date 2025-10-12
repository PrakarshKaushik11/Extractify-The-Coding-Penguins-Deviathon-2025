# api/main.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---- local modules
from crawler.scraper import crawl_domain
from extractor.nlp_pipeline import extract_entities

DATA_DIR = Path("data")
PAGES_PATH = DATA_DIR / "pages.jsonl"
ENTITIES_PATH = DATA_DIR / "entities.json"

app = FastAPI(
    title="Extractify — The Coding Penguins Project (Deviathon 2025)",
    version="1.0.0"
)

# ✅ CORS: open for local dev (tighten later if you want)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # <-- for local dev; replace with explicit list later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Models
# -------------------------
class CrawlRequest(BaseModel):
    domain: str
    keywords: Optional[List[str]] = []
    max_pages: int = 20
    max_depth: int = 2


class ExtractRequest(BaseModel):
    keywords: Optional[List[str]] = []
    target: Optional[str] = "auto"
    # optional: filter threshold you might apply in your UI
    min_score: Optional[float] = 0.0


# -------------------------
# Helpers
# -------------------------
def _read_json(path: Path) -> Any:
    """
    Robust JSON reader:
    - returns None if file missing
    - returns [] if file empty/whitespace
    - returns [] if JSON is invalid/corrupted
    """
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        return json.loads(text)
    except json.JSONDecodeError:
        # corrupted/partial file: treat as empty
        return []
    except Exception:
        # any other unexpected read error
        return []


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    # atomic-ish write to avoid partial files
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


# -------------------------
# Routes
# -------------------------
@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "app": "The Coding Penguins — Entity Extractor",
        "ignore_robots": (os.getenv("CP_IGNORE_ROBOTS", "0") == "1"),
        "semantic_available": True,
    }


@app.post("/crawl")
def crawl(payload: CrawlRequest) -> Dict[str, Any]:
    """
    Crawl a domain and write data/pages.jsonl.
    Returns a small summary with sample URLs and stats.
    """
    try:
        result = crawl_domain(
            domain=payload.domain,
            keywords=payload.keywords or [],
            max_pages=payload.max_pages,
            max_depth=payload.max_depth,
            out_path=str(PAGES_PATH),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract")
def extract(payload: ExtractRequest) -> Dict[str, Any]:
    """
    Run the extractor over data/pages.jsonl and write data/entities.json.
    Returns entities in the response as well.
    """
    if not PAGES_PATH.exists():
        raise HTTPException(status_code=400, detail="No pages found. Run /crawl first.")
    try:
        out = extract_entities(
            pages_path=str(PAGES_PATH),
            entities_path=str(ENTITIES_PATH),
            keywords=payload.keywords or [],
            target=payload.target or "auto",
        )
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extractor error: {e}")


@app.get("/results")
def results() -> List[Dict[str, Any]]:
    """
    Read the last saved entities from data/entities.json.
    Never crashes: returns [] if missing/invalid.
    """
    data = _read_json(ENTITIES_PATH)
    if data is None:
        return []
    # allow both {"entities": [...]} or plain list
    if isinstance(data, dict) and "entities" in data:
        return data["entities"]
    if isinstance(data, list):
        return data
    # fallback if unexpected structure
    return []


@app.post("/crawl-and-extract")
def crawl_and_extract(payload: CrawlRequest) -> Dict[str, Any]:
    """
    Convenience endpoint used by the UI button: crawls then extracts.
    """
    crawl_result = crawl_domain(
        domain=payload.domain,
        keywords=payload.keywords or [],
        max_pages=payload.max_pages,
        max_depth=payload.max_depth,
        out_path=str(PAGES_PATH),
    )
    extract_result = extract_entities(
        pages_path=str(PAGES_PATH),
        entities_path=str(ENTITIES_PATH),
        keywords=payload.keywords or [],
        target="auto",
    )
    return {"crawl": crawl_result, "extract": extract_result}
