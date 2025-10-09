# extractor/nlp_pipeline.py
import argparse, json
from pathlib import Path
import spacy
from spacy.matcher import PhraseMatcher

# local import (works whether run as script or module)
try:
    from . import rules
except ImportError:
    import rules  # fallback when run as a script directly

def ensure_model(name: str = "en_core_web_sm"):
    """Load spaCy model; download if missing."""
    try:
        return spacy.load(name)
    except OSError:
        from spacy.cli import download
        download(name)
        return spacy.load(name)

def load_pages(path: str):
    """Yield page records from JSONL (one JSON per line)."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def build_title_matcher(nlp):
    """Create a phrase matcher for designations (case-insensitive)."""
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(p) for p in rules.TITLE_PATTERNS]
    matcher.add("TITLE", patterns)
    return matcher

def _link_person_to_nearest_title(doc, title_spans, keyword_hit: bool):
    results = []
    persons = [ent for ent in doc.ents if ent.label_ == "PERSON"]
    for p in persons:
        nearest, dist = None, 10**9
        for t in title_spans:
            d = abs(t.start - p.start)
            if d < dist:
                dist, nearest = d, t
        if nearest:
            # base confidence: closer = better; keyword gives small boost
            base = 0.6 + (0.3 * (1.0 / (1 + dist)))
            if keyword_hit:
                base += 0.1
            conf = max(0.0, min(1.0, base))
            results.append((p.text, nearest.text, round(conf, 2)))
    return results

def process_page(nlp, matcher, page, keywords):
    text = page.get("text") or ""
    if not text.strip():
        return []
    doc = nlp(text)
    matches = matcher(doc)
    title_spans = [doc[s:e] for _, s, e in matches]
    keyword_hit = any(k.lower() in text.lower() for k in keywords) if keywords else False

    linked = _link_person_to_nearest_title(doc, title_spans, keyword_hit)
    out = []
    for name, title, conf in linked:
        out.append({
            "name": name,
            "type": "PERSON",
            "designation": title,
            "url": page.get("url"),
            "context": page.get("title"),
            "confidence": conf,
            "found_by": ["spacy_ner", "title_matcher"]
        })
    return out

def run(input_path: str, out_path: str, keywords: list[str]):
    """Public entrypoint used by API and CLI."""
    nlp = ensure_model()
    matcher = build_title_matcher(nlp)

    entities = []
    pages = list(load_pages(input_path))
    for page in pages:
        entities.extend(process_page(nlp, matcher, page, keywords))

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"entities": entities}, f, ensure_ascii=False, indent=2)
    print(f"[NLP] Pages: {len(pages)} | Entities: {len(entities)} | Saved: {out_path}")

def _cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to data/pages.jsonl")
    ap.add_argument("--out", default="data/entities.json")
    ap.add_argument("--keywords", default="")
    args = ap.parse_args()
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    run(args.input, args.out, keywords)

if __name__ == "__main__":
    _cli()
