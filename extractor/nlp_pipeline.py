# extractor/nlp_pipeline.py
from __future__ import annotations

import json
import os
import re
from typing import List, Dict, Any, Iterable

import spacy

# lightweight English NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Allow running even if the model wasn't pre-downloaded (will be slower/no NER)
    nlp = spacy.blank("en")
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")


def _iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


TITLE_HINTS = [
    # generic public-sector titles
    r"\b(attorney general|assistant attorney general|deputy attorney|solicitor general|secretary|minister|judge|chief|commissioner|director|deputy director|under\s+secretary)\b",
    # alumni-ish cues
    r"\b(alumni|alumnus|alumna|batch of|class of|convocation)\b",
]


def _score(snippet: str, keywords: List[str]) -> float:
    score = 0.0
    low = snippet.lower()
    for kw in keywords:
        if kw.lower() in low:
            score += 0.2
    return min(score + 0.5, 1.0)  # base weight


def extract_entities(
    pages_path: str,
    entities_path: str,
    keywords: List[str],
    target: str = "auto",
) -> Dict[str, Any]:
    """
    Reads pages.jsonl, runs a hybrid regex + spaCy PERSON pass,
    and writes entities.json. Returns a dict with domain/pages/entities.
    """
    entities: List[Dict[str, Any]] = []
    pages = list(_iter_jsonl(pages_path))
    domain = pages[0]["url"].split("/")[2] if pages else ""

    patterns = [re.compile(p, re.I) for p in TITLE_HINTS]

    for p in pages:
        text = p.get("text") or ""
        if not text:
            continue

        # quick filter: only process texts that hit any hint
        if not any(pat.search(text) for pat in patterns):
            continue

        # sentence-level scan
        doc = nlp(text[:300000])  # safety cap
        sents = [s.text.strip() for s in getattr(doc, "sents", [doc])]

        for sent in sents:
            if not any(pat.search(sent) for pat in patterns):
                continue

            # find persons
            names: List[str] = []
            if "ner" in nlp.pipe_names:
                d2 = nlp(sent)
                names = [ent.text for ent in d2.ents if ent.label_ == "PERSON"]

            # naive title capture near names
            # e.g., "... John Doe, Assistant Attorney General, ... "
            m = re.search(
                r"(assistant attorney general|attorney general|deputy attorney|solicitor general|secretary|minister|judge|chief|commissioner|director|deputy director|under\s+secretary)",
                sent,
                re.I,
            )
            title = m.group(1) if m else None

            if not names and not title:
                continue

            # build results (dedupe by (name,title,url))
            if not names:
                names = [""]  # allow title-only rows

            for nm in names:
                item = {
                    "name": nm or None,
                    "title": title.title() if title else None,
                    "org": None,
                    "context_url": p.get("url"),
                    "snippet": sent[:500],
                    "score": round(_score(sent, keywords), 3),
                    "sem_score": None,
                }
                # Filter: keep at least one of name/title present
                if item["name"] or item["title"]:
                    entities.append(item)

    # basic dedupe
    seen = set()
    uniq: List[Dict[str, Any]] = []
    for e in entities:
        key = (e.get("name"), e.get("title"), e.get("context_url"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)

    out = {
        "domain": f"https://{domain}" if domain else "",
        "pages_scanned": len(pages),
        "entities": uniq,
    }

    os.makedirs(os.path.dirname(entities_path), exist_ok=True)
    with open(entities_path, "w", encoding="utf-8") as f:
        json.dump(out["entities"], f, ensure_ascii=False, indent=2)

    return out
