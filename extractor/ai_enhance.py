# extractor/ai_enhance.py
from __future__ import annotations

from typing import List, Dict, Any, Iterable, Tuple, Optional
import re
import math

# Optional deps (all local). We handle absence gracefully.
try:
    from sklearn.cluster import AgglomerativeClustering
    HAVE_SK = True
except Exception:
    HAVE_SK = False

try:
    from rapidfuzz import fuzz
    HAVE_RF = True
except Exception:
    HAVE_RF = False

# Our local model loader (GPU/CPU decided inside)
from ai.local_models import get_ai


# ----------------------------
# Config / candidates
# ----------------------------
# Broad, domain-agnostic labels; extend freely.
CANON_LABELS: List[str] = [
    # public sector / justice
    "Minister", "Prime Minister", "Cabinet Minister", "Minister of State",
    "Judge", "Justice", "Chief Justice", "Magistrate",
    "Attorney General", "Deputy Attorney General", "U.S. Attorney", "Public Prosecutor",
    "Secretary", "Cabinet Secretary", "Home Secretary", "Health Secretary",
    "Commissioner", "Registrar", "Chancellor", "Vice-Chancellor", "Pro Vice-Chancellor",
    # academia / research / orgs
    "Director", "Dean", "Professor", "Scientist", "Researcher",
    "Organization", "Department", "Agency",
    # generic fallbacks
    "Person", "Leader", "Executive", "Manager", "Engineer"
]

# Cache for SBERT embeddings to avoid re-encoding identical strings
_EMB_CACHE: dict[str, Any] = {}


# ----------------------------
# Helpers
# ----------------------------
def _sentences(text: str) -> List[str]:
    """Lightweight sentence splitter."""
    if not isinstance(text, str) or not text.strip():
        return []
    # Split on punctuation that ends sentences; keep it simple and robust.
    parts = re.split(r"(?<=[\.\?\!])\s+", text.strip())
    # Filter very short/garbage sentences
    return [re.sub(r"\s+", " ", s.strip()) for s in parts if len(s.strip()) > 10]


def _score_sentence(s: str, name: str, keywords: List[str]) -> float:
    """Score a sentence by name & keyword presence + fuzzy overlap."""
    score = 0.0
    name = (name or "").strip()
    if name and name.lower() in s.lower():
        score += 0.6
    if keywords:
        hit = sum(1 for k in keywords if k and k.lower() in s.lower())
        score += min(0.3, 0.1 * hit)
    if HAVE_RF:
        # Fuzzy overlap against query "name + keywords"
        q = " ".join([name] + keywords)
        score += 0.1 * (fuzz.token_set_ratio(s, q) / 100.0)
    return score


def best_sentence_for_snippet(full_text: str, name: str, keywords: List[str]) -> str:
    """Pick a single logical sentence as the snippet."""
    sents = _sentences(full_text)[:80]  # cap for speed
    if not sents:
        # fallback: compact chunk
        return re.sub(r"\s+", " ", (full_text or "").strip())[:400]
    best = max(sents, key=lambda s: _score_sentence(s, name, keywords or []))
    return best[:400]


def _embed_cached(texts: List[str]) -> Any:
    """SBERT encode with caching (each string cached individually)."""
    ai = get_ai()
    to_compute = []
    idx_map = []
    for i, t in enumerate(texts):
        key = t or ""
        if key not in _EMB_CACHE:
            to_compute.append(key)
            idx_map.append(i)
    if to_compute:
        vecs = ai.sbert.encode(to_compute, convert_to_numpy=True, normalize_embeddings=True)
        for k, v in zip(to_compute, vecs):
            _EMB_CACHE[k] = v
    return [_EMB_CACHE[t or ""] for t in texts]


def sbert_similarity(q: str, docs: List[str]) -> List[float]:
    """Cosine similarity via normalized dot product."""
    if not docs:
        return []
    import numpy as np
    qv = _embed_cached([q])[0]
    dvs = _embed_cached(docs)
    # (qv ⋅ dv)
    sims = [float(qv @ dv) for dv in dvs]
    # Bound to [0,1] just in case of tiny numeric drift
    return [max(0.0, min(1.0, s)) for s in sims]


def _name_distance(a: str, b: str) -> float:
    """Distance for clustering; smaller means closer."""
    if not a or not b:
        return 1.0
    a, b = a.strip(), b.strip()
    if HAVE_RF:
        sim = fuzz.token_sort_ratio(a, b) / 100.0
    else:
        # crude fallback: Jaccard on tokens
        ta, tb = set(a.lower().split()), set(b.lower().split())
        inter = len(ta & tb)
        union = len(ta | tb) or 1
        sim = inter / union
    return 1.0 - sim


def cluster_by_name(entities: List[Dict[str, Any]]) -> List[List[int]]:
    """Cluster entities by (name) similarity; return index groups."""
    n = len(entities)
    if n == 0:
        return []
    if not HAVE_SK or n < 3:
        # trivial grouping: each item alone
        return [[i] for i in range(n)]

    import numpy as np
    D = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = _name_distance(entities[i].get("name", ""), entities[j].get("name", ""))
            D[i, j] = D[j, i] = d

    # 0.3 distance == ~70% name similarity; tuneable
    model = AgglomerativeClustering(
        n_clusters=None,
        affinity="precomputed",
        linkage="average",
        distance_threshold=0.30,
    )
    labels = model.fit_predict(D)
    groups: Dict[int, List[int]] = {}
    for idx, lab in enumerate(labels):
        groups.setdefault(lab, []).append(idx)
    return list(groups.values())


def infer_label_zsl(text: str, candidate_labels: Optional[List[str]] = None) -> str:
    """Infer label with local zero-shot classifier; falls back to simple heuristics."""
    labels = candidate_labels or CANON_LABELS
    try:
        ai = get_ai()
        res = ai.zsl(text or "", labels, multi_label=False)
        if isinstance(res, dict) and res.get("labels"):
            return res["labels"][0]
    except Exception:
        pass
    # Heuristic fallback
    t = (text or "").lower()
    if "minister" in t: return "Minister"
    if "secretary" in t: return "Secretary"
    if "chief justice" in t or "justice" in t or "judge" in t: return "Judge"
    if "professor" in t or "research" in t or "faculty" in t: return "Professor"
    return "Person"


# ----------------------------
# Main enhancer
# ----------------------------
def enhance_entities(
    pages: List[Dict[str, Any]],
    raw: List[Dict[str, Any]],
    keywords: List[str],
    candidate_labels: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Offline AI pass over raw candidates:
      - map/propagate URL
      - pick a meaningful single-sentence snippet
      - infer flexible type via local zero-shot NLI
      - compute semantic similarity for reranking
      - cluster + dedupe by name; keep best in each cluster
    """
    if not raw:
        return []

    # Map URL->text for snippet selection
    text_by_url = {p.get("url"): p.get("text", "") for p in pages if p.get("url")}
    kwords = [k for k in (keywords or []) if isinstance(k, str) and k.strip()]

    enriched: List[Dict[str, Any]] = []
    for e in raw:
        name = (e.get("name") or "").strip()
        url = e.get("url") or e.get("context_url") or ""
        full_text = text_by_url.get(url, "") or e.get("snippet", "") or ""

        # Choose best sentence as snippet
        snip = best_sentence_for_snippet(full_text, name, kwords)

        # Build a context string for labeling
        zsl_text = f"{name}. {snip}" if snip else name
        inferred = infer_label_zsl(zsl_text, candidate_labels)

        # Semantic relevance score (name vs snippet)
        sim = 0.0
        try:
            sims = sbert_similarity(name, [snip]) if snip else [0.0]
            sim = float(max(sims[0], 0.0))
        except Exception:
            pass

        # Keyword coverage bonus
        kw_bonus = 0.0
        if kwords:
            hits = sum(1 for k in kwords if k.lower() in snip.lower())
            kw_bonus = min(0.3, 0.1 * hits)

        base = float(e.get("score", 0.0) or 0.0)
        final_score = max(base, 0.7 * sim + kw_bonus)

        enriched.append({
            **e,
            "url": url,
            "type": inferred,
            "snippet": snip,
            "score": final_score,
        })

    # Cluster & dedupe by name similarity; keep highest score per cluster
    clusters = cluster_by_name(enriched)
    selected: List[Dict[str, Any]] = []
    clustered = set()
    for group in clusters:
        if not group:
            continue
        best = max((enriched[i] for i in group), key=lambda r: (r.get("score") or 0.0))
        selected.append(best)
        clustered.update(group)

    # Add any non-clustered items (small N or no sklearn path)
    for i in range(len(enriched)):
        if i not in clustered:
            selected.append(enriched[i])

    # Final unique by (name, url)
    seen = set()
    out: List[Dict[str, Any]] = []
    for r in selected:
        k = (str(r.get("name", "")).strip().lower(), str(r.get("url", "")).strip().lower())
        if k in seen:
            continue
        seen.add(k)
        out.append(r)

    return out
