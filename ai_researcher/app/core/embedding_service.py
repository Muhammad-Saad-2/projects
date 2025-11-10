from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np 
from app.utils.logger import get_logger


logger = get_logger(__name__)



class EmbeddingService:

    def __init__(self, model_name:str = "all-MiniLM-L6-v2"):
        logger.info(f"Initializing embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Embedding Model Loaded Successfully ")

    
    def chunk_document(self, document: str , chunk_size: int = 500, overlap: int = 50)-> List[str]:
        chunks = []
        start = 0
        while start < len(document):
            end = min(start + chunk_size, len(document))
            chunks.append(document[start:end])
            start += chunk_size - overlap
        logger.info(f"Document chunked into {len(chunks)} segments (chunk_size={chunk_size}, overlap={overlap}).")
        return chunks

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        logger.info(f"Generating embeddings for {len(texts)} text chunks...")
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings


