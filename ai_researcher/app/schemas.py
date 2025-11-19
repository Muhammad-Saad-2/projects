from pydantic import BaseModel, Field 
from typing import List, Dict, Optional, Any
from typing import Optional


class QueryRequest(BaseModel):
    query:str 
    similarity_threshold: Optional[float] = Field(default=0.5, ge=0.3, le=0.6)
    top_k: int = 5 


class SearchResult(BaseModel):
    score: float
    # similarity_threshold: str 
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    status: str
    source: str
    results: List[SearchResult]
    summary: str
    # results: Any
    message: Optional[str] = None
