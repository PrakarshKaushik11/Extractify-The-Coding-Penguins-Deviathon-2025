# extractor/nlp_pipeline.py
from __future__ import annotations

import re
from typing import Dict, List, Any

import spacy

# Load once
_NLP = spacy.load("en_core_web_sm")

# Alumni cues (for small boosts / fallbacks)
from extractor.type_filters import ALUMNI_HINTS, DEGREE_RE, YEAR_RE

TITLE_WORDS = [
    "attorney general","assistant attorney general","solicitor general","minister","secretary",
    "judge","justice","director","dean","registrar","professor","associate professor",
    "assistant professor","lecturer","chancellor","vice chancellor","hod","head of department",
]

def _rule_score(text: str, keywords: List[str]) -> float:
    score = 0.45
    low = text.lower()
    for k in keywords or []:
        if k and k.lower() in low:
            score += 0.1
    score = min(0.95, score)
    return score

def _boost_by_alumni(text: str) -> float:
    if ALUMNI_HINTS.search(text):
        return 0.25
    if DEGREE_RE.search(text) and YEAR_RE.search(text):
        return 0.20
    return 0.0

def _best_title_span(text: str) -> str:
    low = text.lower()
    for t in TITLE_WORDS:
        if t in low:
            return t.title()
    return ""

def extract_entities_from_texts(pages: List[Dict[str, str]], keywords: List[str]) -> List[Dict[str, Any]]:
    """NER + rule-based title/keyword matcher + alumni fallback."""
    out: List[Dict[str, Any]] = []

    for page in pages:
        url = page.get("url")
        raw = page.get("text","")
        if not raw:
            continue

        # 1) spaCy NER
        doc = _NLP(raw)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 5:
                snip_start = max(0, ent.start_char - 120)
                snip_end = min(len(raw), ent.end_char + 120)
                snippet = raw[snip_start:snip_end]
                title = _best_title_span(snippet)
                score = _rule_score(snippet, keywords)
                score += _boost_by_alumni(snippet)
                out.append({
                    "name": ent.text.strip(),
                    "title": title or "Person",
                    "org": None,
                    "context_url": url,
                    "snippet": snippet.strip(),
                    "score": round(min(0.99, score), 3),
                })

        # 2) Title-first extraction (when names are not tagged)
        for t in TITLE_WORDS:
            if t in raw.lower():
                # naive capture up to 6 tokens before title as a name-like phrase
                pattern = re.compile(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,5})[^\.]{0,50}" + re.escape(t), re.I)
                for m in pattern.finditer(raw):
                    name = m.group(1).strip()
                    snippet = raw[max(0, m.start()-120):m.end()+120]
                    score = 0.55 + _boost_by_alumni(snippet)
                    out.append({
                        "name": name,
                        "title": t.title(),
                        "org": None,
                        "context_url": url,
                        "snippet": snippet.strip(),
                        "score": round(min(0.99, score), 3),
                    })

        # 3) Alumni fallback (div/card-heavy pages)
        # Names followed by batch/class or degree+year
        pattern = re.compile(
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b(?:[^\.]{0,50}(?:Batch\s*of|Class\s*of)\s*(19|20)\d{2})?",
            re.M
        )
        for m in pattern.finditer(raw):
            name = m.group(1).strip()
            if len(name.split()) < 2 or name.isupper():
                continue
            snippet = raw[max(0, m.start()-80):m.end()+80]
            if not (ALUMNI_HINTS.search(snippet) or (DEGREE_RE.search(snippet) and YEAR_RE.search(snippet))):
                continue
            score = 0.60 + _boost_by_alumni(snippet)
            out.append({
                "name": name,
                "title": "Alumni",
                "org": None,
                "context_url": url,
                "snippet": snippet.strip(),
                "score": round(min(0.99, score), 3),
            })

    # light dedupe by (name, url)
    seen = set()
    deduped = []
    for e in out:
        key = (e.get("name"), e.get("context_url"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    return deduped
