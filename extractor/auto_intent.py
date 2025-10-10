# extractor/auto_intent.py
from typing import List, Set
import re

PERSON_HINTS = re.compile(r"\b(person|people|name|member|leader|minister|secretary|judge|alumni|alumnus|alumna)\b", re.I)
ALUMNI_HINTS = re.compile(r"\b(alumni|alumnus|alumna|graduate|class of|batch of|pass ?out|convocation)\b", re.I)
JUDGE_HINTS  = re.compile(r"\b(judge|justice|court)\b", re.I)
MIN_HINTS    = re.compile(r"\b(minister|secretary|cabinet)\b", re.I)
TECH_HINTS   = re.compile(r"\b(api|sdk|framework|library|python|java|docker|kubernetes|ml|nlp|transformer)\b", re.I)
ORG_HINTS    = re.compile(r"\b(department|ministry|company|university|institute|office|division)\b", re.I)
LOC_HINTS    = re.compile(r"\b(state|district|city|country|region|campus)\b", re.I)

def infer_types(query_terms: List[str]) -> List[str]:
    q = " ".join(query_terms)
    labels: Set[str] = set()
    if PERSON_HINTS.search(q): labels.add("person")
    if ALUMNI_HINTS.search(q): labels.add("alumni")
    if JUDGE_HINTS.search(q):  labels.add("judge")
    if MIN_HINTS.search(q):    labels.add("minister")
    if TECH_HINTS.search(q):   labels.add("tech_term")
    if ORG_HINTS.search(q):    labels.add("org")
    if LOC_HINTS.search(q):    labels.add("location")
    if not labels:
        labels.add("generic")
    return list(labels)
