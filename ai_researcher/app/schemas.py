from pydantic import BaseModel, Field 
from typing import List, Dict, Optional, Any


class QueryRequest(BaseModel):
    query:str 
    similarity_threshold: Optional[float]
    top_k: Optional[float] = Field(default=0.75, ge=0.5, le=0.75)


class SearchResult(BaseModel):
    score: float
    similarity: str
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    status: str
    source: str
    results: List[SearchResult]
    summary: str
    message: Optional[str] = None
