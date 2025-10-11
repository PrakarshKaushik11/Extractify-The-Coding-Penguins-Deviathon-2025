# ai/local_models.py
from __future__ import annotations
import os
import torch
import spacy
from typing import Optional

from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# Prefer GPU if available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE_ID = 0 if DEVICE == "cuda" else -1
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

# Model names/paths (can be local dirs; set via env to run fully offline)
SBERT_NAME = os.getenv("LOC_SBERT", "sentence-transformers/all-MiniLM-L6-v2")
ZSL_NAME   = os.getenv("LOC_ZSL",   "facebook/bart-large-mnli")

class LocalAI:
    def __init__(self):
        # --- SpaCy (CPU; it’s light and thread-safe)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = spacy.blank("en")
            if "sentencizer" not in self.nlp.pipe_names:
                self.nlp.add_pipe("sentencizer")

        # --- Sentence Embeddings (SBERT)
        # SentenceTransformer accepts a device string; it moves the whole encoder.
        self.sbert = SentenceTransformer(SBERT_NAME, device=DEVICE)  # uses CUDA if available

        # --- Zero-shot NLI (for labeling)
        tok = AutoTokenizer.from_pretrained(ZSL_NAME)
        mdl = AutoModelForSequenceClassification.from_pretrained(
            ZSL_NAME,
            torch_dtype=DTYPE,
        )
        mdl.to(DEVICE)
        self.zsl = pipeline(
            "zero-shot-classification",
            model=mdl,
            tokenizer=tok,
            device=DEVICE_ID,  # 0 for CUDA, -1 for CPU
            truncation=True
        )

AI = None

def get_ai() -> LocalAI:
    global AI
    if AI is None:
        AI = LocalAI()
    return AI
