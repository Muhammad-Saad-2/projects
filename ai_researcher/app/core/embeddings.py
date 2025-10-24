from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np 



class EmbeddingService:

    def __init__(self, model_name:str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    
    def chunk_document(self, document: str , chunk_size: int = 500, overlap: int = 50)-> List[str]:
        chunks = []
        start = 0
        while start < len(document):
            end = min(start + chunk_size, len(document))
            chunks.append(document[start:end])
            start += chunk_size - overlap
        return chunks

    def get_embeddings(self, text: List[str]) -> np.ndarray:
        
        """Encodes a list of texts into their vector embeddings."""

        embeddings = self.model.encode(text, convert_to_numpy=True)
        return embeddings


