from pydantic import BaseModel, Field 
from typing import List, Dict, Optional, Any


class QueryRequest(BaseModel):
    query:str 
    similarity_threshold: float = Field(default=0.75, ge=0.3, le=0.75)
    top_k: int = 5 


class SearchResult(BaseModel):
    score: float
    # similarity_threhold: str
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    status: str
    source: str
    results: List[SearchResult]
    summary: str
    message: Optional[str] = None
