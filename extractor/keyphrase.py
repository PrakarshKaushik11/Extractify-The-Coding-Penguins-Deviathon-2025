# extractor/keyphrase.py
from typing import List
import yake

def top_keyphrases(texts: List[str], k: int = 12) -> List[str]:
    if not texts:
        return []
    sample = "\n".join(texts[:6])[:200_000]
    kw = yake.KeywordExtractor(lan="en", n=1, top=k//2)
    kws1 = [w for w, _ in kw.extract_keywords(sample)]
    kw2 = yake.KeywordExtractor(lan="en", n=2, top=k)
    kws2 = [w for w, _ in kw2.extract_keywords(sample)]
    seen, out = set(), []
    for t in kws2 + kws1:
        t = t.strip()
        if t and t.lower() not in seen:
            seen.add(t.lower()); out.append(t)
    return out[:k]
