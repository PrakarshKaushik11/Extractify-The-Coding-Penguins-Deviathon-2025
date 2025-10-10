# extractor/semantic_ranker.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Iterable

from rank_bm25 import BM25Okapi

try:
    from sentence_transformers import SentenceTransformer, util
    _HAS_ST = True
except Exception:
    _HAS_ST = False

@dataclass
class RankedChunk:
    url: str
    text: str
    score_bm25: float
    sem_score: float

class SemanticRanker:
    """Hybrid BM25 + MiniLM ranker. Fully local."""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name) if _HAS_ST else None

    @staticmethod
    def _sentences(docs: Iterable[str]) -> List[str]:
        sents: List[str] = []
        for t in docs:
            t = (t or "").strip()
            if not t:
                continue
            sents.append(t)
        return sents

    def rank(self, docs: List[Dict], query_terms: List[str], require_alumni: bool = False) -> List[RankedChunk]:
        texts = [d.get("text","") for d in docs]
        urls = [d.get("url","") for d in docs]

        # BM25 (token-based)
        tokenized_corpus = [t.split() for t in texts]
        bm25 = BM25Okapi(tokenized_corpus)
        q = " ".join(query_terms) if query_terms else ""
        bm25_scores = bm25.get_scores(q.split()) if q else [0.0]*len(texts)

        # Semantic (MiniLM)
        sem_scores = [0.0]*len(texts)
        if self.model and q:
            qv = self.model.encode([q], normalize_embeddings=True, convert_to_tensor=True)
            dv = self.model.encode(texts, normalize_embeddings=True, convert_to_tensor=True)
            sim = util.cos_sim(qv, dv)[0]
            sem_scores = [float(x) for x in sim]

        ranked: List[RankedChunk] = []
        for i, (u, t) in enumerate(zip(urls, texts)):
            if require_alumni:
                # small bias
                tl = (u + " " + t[:400]).lower()
                if ("alumni" not in tl) and ("convocation" not in tl) and ("graduat" not in tl):
                    continue
            ranked.append(RankedChunk(u, t, bm25_scores[i], sem_scores[i]))

        ranked.sort(key=lambda r: (0.4*r.score_bm25 + 0.6*r.sem_score), reverse=True)
        return ranked
