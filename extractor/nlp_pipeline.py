# extractor/nlp_pipeline.py
from __future__ import annotations

import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse
from extractor.ai_enhance import enhance_entities


# Local NER (no cloud)
import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en")
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")

from .rules import TITLE_PATTERNS

# ---------- normalization & filters ----------
NOISE_NAMES = [
    "admission","apply now","contact us","careers","download",
    "privacy","terms","campus course","course list",
    "mathura campus","noida campus course","home","login","register"
]
ROLE_NORMALIZE = {
    "Vice Chancellor": "Vice-Chancellor",
    "Pro Vice Chancellor": "Pro Vice-Chancellor",
    "Chief Justice": "Chief Justice",
    "Judge": "Judge",
    "Director": "Director",
    "Registrar": "Registrar",
    "Dean": "Dean",
    "Professor": "Professor",
}

# Role whitelist buckets (expand as needed)
ROLE_WHITELIST_BASE = {
    "minister": {
        "minister","prime minister","cabinet minister","union minister","minister of state","mos"
    },
    "judge": {
        "judge","justice","chief justice","magistrate"
    },
    "secretary": {
        "secretary","cabinet secretary","home secretary","health secretary","education secretary",
        "principal secretary","joint secretary","additional secretary"
    },
}
def build_role_whitelist(keywords: List[str]) -> set[str]:
    wl: set[str] = set()
    for k in (keywords or []):
        wl |= {r for r in ROLE_WHITELIST_BASE.get(k.lower(), set())}
    # If no keywords provided, allow all buckets
    return wl or set().union(*ROLE_WHITELIST_BASE.values())

TITLE_RE = re.compile(r"|".join([re.escape(t) for t in TITLE_PATTERNS]), re.I)
NAME_NEARBY_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b")

def _noisy_name(s: Any) -> bool:
    if not isinstance(s, str) or not s.strip():
        return True
    s2 = s.lower().strip()
    return any(tok in s2 for tok in NOISE_NAMES)

def _boilerplate_snippet(snippet: Any) -> bool:
    if not isinstance(snippet, str):
        return True
    s = snippet.lower()
    keys = ["admission","careers","contact us","select state","select branch"]
    return sum(k in s for k in keys) >= 2

def _fix_url(u: Optional[str]) -> Optional[str]:
    if not isinstance(u, str) or not u.strip():
        return None
    u = u.strip()
    if not re.match(r"^https?://", u):
        u = "https://" + u.lstrip("/")
    return u

def _snippet_around(text: str, start: int, end: int, window: int = 240) -> str:
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    snip = text[lo:hi].strip()
    return re.sub(r"\s+", " ", snip)

def _normalize_role(x: Optional[str]) -> Optional[str]:
    if not isinstance(x, str):
        return None
    x = x.strip()
    return ROLE_NORMALIZE.get(x, x)

def _is_personish(name: str) -> bool:
    if not isinstance(name, str): 
        return False
    s = name.strip()
    if len(s) < 3:
        return False
    # reject clearly generic tokens that crept in
    bad = {"department","information","excellence","today","details","videos","programs","government services"}
    if s.lower() in bad:
        return False
    # Simple heuristic: PascalCase tokens like "John Doe" up to 4 words
    return bool(re.fullmatch(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}", s))

def sanitize_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Map fields (context_url→url, title→type), drop noise, require role, dedupe by (name,url).
    """
    cleaned: List[Dict[str, Any]] = []
    seen = set()
    for e in entities:
        e["url"] = e.get("url") or e.get("context_url")
        e["type"] = e.get("type") or e.get("title")
        e["type"] = _normalize_role(e.get("type"))
        e["url"] = _fix_url(e.get("url"))

        if not e.get("type"):                   # must have a role
            continue
        if _noisy_name(e.get("name")):
            continue
        if _boilerplate_snippet(e.get("snippet","")):
            continue

        key = ((e.get("name") or "").strip().lower(), (e.get("url") or "").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(e)
    return cleaned

# ---------- pages loader ----------
def _read_pages_jsonl(pages_path: str) -> List[Dict[str, Any]]:
    pages: List[Dict[str, Any]] = []
    with open(pages_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    pages.append(obj)
            except json.JSONDecodeError:
                pass
    return pages

# ---------- extraction core ----------
def _extract_candidates_from_text(text: str) -> List[Tuple[str, Optional[str], int, int]]:
    """
    Returns (name, role, start_idx, end_idx)
    """
    cands: List[Tuple[str, Optional[str], int, int]] = []

    # 1) Role patterns near capitalized names
    for m in TITLE_RE.finditer(text):
        role = m.group(0)
        span_lo = max(0, m.start() - 220)
        span_hi = min(len(text), m.end() + 220)
        win = text[span_lo:span_hi]
        nm = NAME_NEARBY_RE.search(win)
        if nm:
            name = nm.group(1)
            name_abs_lo = span_lo + nm.start(1)
            name_abs_hi = span_lo + nm.end(1)
            cands.append((name, role, min(name_abs_lo, m.start()), max(name_abs_hi, m.end())))
        else:
            # We’ll later require personish names; keep role-only for now
            cands.append((role, None, m.start(), m.end()))

    # 2) NER fallback/boost
    if nlp.pipe_names:
        doc = nlp(text[:800000])
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG"}:
                cands.append((ent.text, None, ent.start_char, ent.end_char))
    return cands

def _build_entities_for_page(page: Dict[str, Any], role_whitelist: set[str]) -> List[Dict[str, Any]]:
    url = page.get("url") or ""
    text = page.get("text") or ""
    if not isinstance(text, str) or len(text) < 40:
        return []
    out: List[Dict[str, Any]] = []
    for name, role, s, e in _extract_candidates_from_text(text):
        # Must look like a person
        if not _is_personish(name):
            continue

        # If a role was found, gate by whitelist
        role_ok = True
        if role is not None and role_whitelist:
            role_ok = role.strip().lower() in role_whitelist
        if not role_ok:
            continue

        out.append({
            "name": name.strip() if isinstance(name, str) else name,
            "title": role.strip() if isinstance(role, str) else None,   # keep original key
            "org": None,
            "context_url": url,                                         # keep original key
            "snippet": _snippet_around(text, s, e, window=240),
            "score": 0.5,
            "sem_score": None,
        })
    return out

# ---------- public entry ----------
def extract_entities(
    pages_path: str,
    entities_path: str,
    keywords: List[str],
    target: str = "auto",
) -> Dict[str, Any]:
    # 1) Load pages
    pages = _read_pages_jsonl(pages_path)

    # 2) Generate broad raw candidates (your existing _build_entities_for_page)
    raw: List[Dict[str, Any]] = []
    for p in pages:
        raw.extend(_build_entities_for_page(p, role_whitelist=set()))  # pass empty; we won’t hard-limit

    # 3) AI enhancement (local only): infer types, smart snippets, semantic rerank, cluster-dedupe
    entities = enhance_entities(pages, raw, keywords)

    # 4) Write out
    domain = ""
    if pages:
        try:
            from urllib.parse import urlparse
            domain = urlparse(pages[0].get("url", "")).netloc
        except Exception:
            pass

    os.makedirs(os.path.dirname(entities_path), exist_ok=True)
    with open(entities_path, "w", encoding="utf-8") as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)

    return {
        "domain": f"https://{domain}" if domain else "",
        "pages_scanned": len(pages),
        "entities": entities,
        "entities_count": len(entities),
    }
