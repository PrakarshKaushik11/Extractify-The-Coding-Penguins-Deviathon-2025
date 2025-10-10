# extractor/type_filters.py
from __future__ import annotations
import re
from typing import Dict, Any

# Alumni signals (wide coverage for Indian university phrasing)
ALUMNI_HINTS = re.compile(
    r"\b(alumni|alumnus|alumna|alumnae|graduate|convocation|pass\s*out|"
    r"class\s*of\s*(19|20)\d{2}|batch\s*of\s*(19|20)\d{2}|alumni\s+meet|"
    r"alumni\s+association|notable\s+alumni)\b", re.I
)
DEGREE_RE = re.compile(
    r"\b(B\.?\s*Tech|M\.?\s*Tech|BSc|MSc|MBA|BBA|PhD|B\.?\s*Pharm|M\.?\s*Pharm|BCA|MCA)\b", re.I
)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

TECH_RE = re.compile(
    r"\b(api|sdk|library|framework|python|java(script)?|node\.js|docker|kubernetes|ml|nlp|"
    r"transformer|embedding|vector|microservice|rest|graphql|database|postgres|mysql)\b",
    re.I,
)

def allow_entity(e: Dict[str, Any], target_type: str) -> bool:
    if target_type == "generic":
        return True

    text = f"{e.get('name','')} {e.get('title','')} {e.get('snippet','')}"
    url  = (e.get("context_url") or "").lower()
    tlow = text.lower()

    if target_type == "alumni":
        if "alumni" in url:
            return True
        if ALUMNI_HINTS.search(text):
            return True
        if DEGREE_RE.search(text) and YEAR_RE.search(text):
            return True
        if re.search(r"alumni[-_\s]*card|batch\s*of|class\s*of|passed\s*out|convocation", tlow):
            return True
        # require at least a name
        return bool(e.get("name"))

    if target_type == "judge":
        t = (e.get("title") or "").lower()
        return ("judge" in t) or ("justice" in t)

    if target_type == "minister":
        t = (e.get("title") or "").lower()
        return ("minister" in t) or ("secretary" in t)

    if target_type == "tech_term":
        return bool(TECH_RE.search(tlow))

    if target_type == "org":
        return ("university" in tlow) or ("department" in tlow) or ("ministry" in tlow) or ("company" in tlow)

    if target_type == "location":
        return any(k in tlow for k in ["campus", "city", "state", "district", "region", "country"])

    # person: pass if it looks like a name or has role words
    if target_type == "person":
        t = (e.get("title") or "").lower()
        if any(x in t for x in ["professor","director","dean","registrar","lecturer","chancellor","vice chancellor","secretary","minister","judge"]):
            return True
        return bool(e.get("name"))

    return True
