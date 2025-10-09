from pydantic import BaseModel
from typing import Optional

class CrawlRequest(BaseModel):
    domain: str
    max_depth: int = 1
    keywords: Optional[str] = ""

class ExtractRequest(BaseModel):
    input_path: str = "data/pages.jsonl"
    out_path: str = "data/entities.json"
    keywords: Optional[str] = ""
