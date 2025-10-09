import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import CrawlRequest, ExtractRequest
import subprocess, json

app = FastAPI(title="The Coding Penguins API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/crawl")
def crawl(req: CrawlRequest):
    cmd = [
        "python", "crawler/scraper.py",
        "--domain", req.domain,
        "--max_depth", str(req.max_depth),
        "--out", "data/pages.jsonl",
        "--keywords", req.keywords or "",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": out.returncode == 0, "stdout": out.stdout, "stderr": out.stderr}

@app.post("/extract")
def extract(req: ExtractRequest):
    cmd = [
    sys.executable, "extractor/nlp_pipeline.py",
    "--input", req.input_path,
    "--out", req.out_path,
    "--keywords", req.keywords or "",
    ]

    out = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": out.returncode == 0, "stdout": out.stdout, "stderr": out.stderr}

@app.get("/results")
def results():
    try:
        with open("data/entities.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"entities": []}
