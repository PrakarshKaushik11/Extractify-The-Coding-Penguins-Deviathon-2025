from pydantic import BaseModel, Field
from typing import List, Optional

class CrawlRequest(BaseModel):
    domain: str
    keywords: List[str] = Field(default_factory=list)
    max_pages: int = 150
    max_depth: int = 2

class PageDoc(BaseModel):
    url: str
    title: Optional[str] = None
    text: str

class Entity(BaseModel):
    name: str
    title: Optional[str] = None
    org: Optional[str] = None
    context_url: Optional[str] = None
    snippet: Optional[str] = None
    score: float = 0.0

class CrawlAndExtractResponse(BaseModel):
    domain: str
    pages_scanned: int
    entities: List[Entity]
