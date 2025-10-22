# extractor/nlp_pipeline.py
from __future__ import annotations

import json
import os
import re
from typing import List, Dict, Iterable, Optional
import os

# ---------------- NLP setup ----------------
import spacy

# Load spaCy (download once if missing)
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Optional: local semantic model (lazy loading for memory efficiency)
_st_model = None

def _get_st_model():
    """Lazy load SentenceTransformer model only when needed"""
    global _st_model
    if _st_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            pass
    return _st_model


# ---------------- utilities ----------------
def _norm_text(s: str) -> str:
    return " ".join((s or "").split())

def _keywords_list(keywords: Iterable[str] | None) -> list[str]:
    return [k.strip().lower() for k in (keywords or []) if k and k.strip()]

def _semantic_score(text: str, keywords: list[str]) -> float:
    """
    0..1 similarity between a text and the provided keywords.
    Uses SentenceTransformer if available; otherwise falls back to token overlap.
    """
    if not text or not keywords:
        return 0.0
    
    model = _get_st_model()
    if model:
        try:
            from sentence_transformers import util as st_util
            t_emb = model.encode([text], normalize_embeddings=True)
            k_emb = model.encode(["; ".join(keywords)], normalize_embeddings=True)
            sim = float(st_util.cos_sim(t_emb, k_emb)[0][0])  # [-1, 1]
            return max(0.0, min(1.0, (sim + 1.0) / 2.0))
        except Exception:
            pass
    # Fallback
    tset = set(_norm_text(text).lower().split())
    kset = set(keywords)
    return 0.0 if not tset or not kset else len(tset & kset) / max(1, len(kset))

def _window(text: str, start: int, end: int, radius: int = 240) -> str:
    a = max(0, start - radius)
    b = min(len(text), end + radius)
    return text[a:b]


# ------------- pattern helpers -------------
# Title-like fragment near a name (Team cards, bios, etc.)
TITLE_NEAR_RE = re.compile(
    r"(?:^|[\s,;:\-\–\—\(\)\[\]\|])([A-Z][A-Za-z\-/& ]{2,40})",
    flags=re.M
)

# Job/role phrases we want to catch anywhere in the nearby window
JOB_TITLE_RE = re.compile(
    r"\b("
    r"(software|backend|front[- ]?end|full[- ]?stack|platform|data|ml|ai|security|cloud|mobile|android|ios)"
    r"[ -]?(engineer|developer|specialist|architect|lead|manager|mentor|instructor|trainer)"
    r"|product manager|engineering manager|tech( |\-)?lead|cto|ceo|founder|professor|research(er)?"
    r")\b",
    re.I,
)

ORG_HINT_RE = re.compile(r"\b(at|@|from|with)\s+([A-Z][A-Za-z0-9&\-\., ]{2,50})")


def _nearest_org(doc: spacy.tokens.Doc, start_char: int, end_char: int) -> str | None:
    nearest = None
    nearest_dist = 10**9
    for ent in doc.ents:
        if ent.label_ != "ORG":
            continue
        d = min(abs(ent.start_char - end_char), abs(start_char - ent.end_char))
        if d < nearest_dist:
            nearest_dist = d
            nearest = ent.text
    return nearest


# -------- generic candidate extraction ------
def _extract_candidates_from_page(page_text: str, page_url: str) -> list[dict]:
    """
    Build PERSON candidates with nearby title guess + org + rich snippet.
    """
    doc = nlp(page_text)
    out: list[dict] = []

    phone_re = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}")
    address_re = re.compile(r"\d{1,5} [A-Za-z0-9 .,'-]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Blvd|Boulevard|Campus|Building|Block|Sector|Colony|Area)", re.I)
    year_re = re.compile(r"(19|20)\d{2}")

    for ent in doc.ents:
        if ent.label_ != "PERSON":
            continue

        ctx = _window(page_text, ent.start_char, ent.end_char, radius=260)

        # Title guess from nearby TitleCase or explicit job phrases
        title_guess = None
        m_job = JOB_TITLE_RE.search(ctx)
        if m_job:
            title_guess = m_job.group(0).strip()
        else:
            for m in TITLE_NEAR_RE.finditer(ctx):
                frag = m.group(1).strip()
                if ent.text in frag:
                    continue
                if 2 <= len(frag.split()) <= 7:
                    title_guess = frag
                    break

        # Organization (spaCy ORG nearest or "at/@" pattern)
        org_guess = _nearest_org(doc, ent.start_char, ent.end_char)
        if not org_guess:
            m_org = ORG_HINT_RE.search(ctx)
            if m_org:
                org_guess = m_org.group(2).strip()

        snippet = ctx.strip()[:360]

        # Extract phone, address, passing year from context
        phone = None
        address = None
        passing_year = None
        m_phone = phone_re.search(ctx)
        if m_phone:
            phone = m_phone.group(0)
        m_addr = address_re.search(ctx)
        if m_addr:
            address = m_addr.group(0)
        m_year = year_re.search(ctx)
        if m_year:
            passing_year = m_year.group(0)

        out.append({
            "name": ent.text.strip(),
            "title": title_guess,
            "org": org_guess,
            "context_url": page_url,
            "snippet": snippet,
            "phone": phone,
            "address": address,
            "passing_year": passing_year,
            "_features": {
                "has_title": 1.0 if title_guess else 0.0,
                "has_org": 1.0 if org_guess else 0.0,
                "richness": min(1.0, len(ctx) / 450.0),
            }
        })
    return out


# ----------------- scoring ------------------
def _page_title_boost(url: str) -> float:
    # cheap heuristic using URL path hints
    return 0.15 if re.search(r"(team|people|staff|mentor|leadership|about|profile|careers)", url, re.I) else 0.0

def _score_candidate(c: dict, keywords: list[str]) -> float:
    """
    Score (0..1) using:
      - semantic similarity to keywords (if any)
      - structural cues (title/org presence, snippet richness)
      - small URL/section boost for team/people pages
    """
    title = c.get("title") or ""
    snippet = c.get("snippet") or ""
    url = c.get("context_url") or ""
    text_for_sem = f"{title}. {snippet}".strip()

    sem = _semantic_score(text_for_sem, keywords) if keywords else 0.0
    feats = c.get("_features", {})
    has_title = float(feats.get("has_title", 0.0))
    has_org = float(feats.get("has_org", 0.0))
    richness = float(feats.get("richness", 0.0))
    url_boost = _page_title_boost(url)

    if keywords:
        score = 0.60 * sem + 0.20 * has_title + 0.10 * has_org + 0.10 * (richness + url_boost)
    else:
        score = 0.45 * has_title + 0.20 * has_org + 0.35 * (richness + url_boost)

    return max(0.0, min(1.0, score))


# ----------------- main API -----------------
def extract_entities(
    pages_path: str,
    entities_path: str,
    keywords: List[str] | None = None,
    target: str = "auto",
    cancel_path: Optional[str] = None,
) -> Dict[str, object]:
    """
    Flexible extractor for any site + any keyword(s) (or none).
    Reads JSONL from pages_path; incrementally writes JSON array to entities_path.

    Behavior change: entities_path is updated after each processed page so that the
    frontend can poll /api/results and see results grow in real time.
    """
    kw = _keywords_list(keywords)

    # Prepare output file (empty JSON array) for incremental updates
    os.makedirs(os.path.dirname(entities_path), exist_ok=True)
    try:
        with open(entities_path, "w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception:
        pass

    # De-dup store across pages
    best: dict[tuple, dict] = {}
    pages_scanned = 0
    first_page_url = ""

    def _emit_entities():
        # materialize current best set as sorted list and persist to file
        entities_list = [
            {
                "name": c["name"],
                "type": c.get("title") or "Person",
                "url": c.get("context_url"),
                "snippet": c.get("snippet"),
                "score": round(float(c["_score"]), 3),
                "phone": c.get("phone"),
                "address": c.get("address"),
                "passing_year": c.get("passing_year"),
            }
            for c in sorted(best.values(), key=lambda x: x["_score"], reverse=True)
        ]
        try:
            with open(entities_path, "w", encoding="utf-8") as f:
                json.dump(entities_list, f, ensure_ascii=False, indent=2)
        except Exception:
            # ignore transient IO errors and continue
            pass
        return entities_list

    # Stream pages one by one
    with open(pages_path, "r", encoding="utf-8") as f:
        for line in f:
            # cooperative cancellation
            if cancel_path and os.path.exists(cancel_path):
                break
            line = line.strip()
            if not line:
                continue
            try:
                p = json.loads(line)
            except Exception:
                continue

            txt = p.get("text") or ""
            url = p.get("url") or ""
            if not first_page_url and url:
                first_page_url = url
            if not txt:
                pages_scanned += 1
                continue

            # build candidates for this page
            for c in _extract_candidates_from_page(txt, url):
                c["_score"] = _score_candidate(c, kw)
                if kw and _semantic_score((c.get("title") or "") + " " + (c.get("snippet") or ""), kw) < 0.15:
                    continue
                key = (c["name"].lower(), (c.get("title") or "").lower(), c.get("context_url") or "")
                if key not in best or c["_score"] > best[key]["_score"]:
                    best[key] = c

            pages_scanned += 1
            # Persist after each page to support real-time UI
            _emit_entities()

    # Final materialization
    entities = _emit_entities()

    # infer domain from first page
    domain = ""
    try:
        from urllib.parse import urlparse
        if first_page_url:
            domain = urlparse(first_page_url).netloc
    except Exception:
        pass

    return {
        "domain": f"https://{domain}" if domain else "",
        "pages_scanned": pages_scanned,
        "entities": entities,
        "entities_count": len(entities),
        "cancelled": 1 if (cancel_path and os.path.exists(cancel_path)) else 0,
    }
