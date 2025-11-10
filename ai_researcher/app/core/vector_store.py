import os 
import json
import numpy as np
import faiss  #type: ignore
from typing import List, Dict, Optional
from app.core.embedding_service import EmbeddingService 
from app.utils.logger import get_logger

logger = get_logger(__name__)


#path setup for FAISS index and metadata storga 
VECTOR_INDEX_PATH = "./app/data/vector_store/index.faiss"
METADATA_PATH = "./app/data/vector_store/metadata.json" 



class VectorStore:
    def __init__(self, embedding_dem: int = 384, embedding_service: Optional['EmbeddingService'] = None): 
        self.embedding_dim = embedding_dem
        self.index_path = VECTOR_INDEX_PATH
        self.metadata_path = METADATA_PATH

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_service = embedding_service or EmbeddingService(model_name="all-MiniLM-L6-v2")
        self.index, self.metadata = self._load_or_initialize()

    
    def _load_or_initialize(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            logger.info(f"Loaded existing FAISS index with {len(metadata)} entries.")    
        else:
            index = faiss.IndexFlatL2(self.embedding_dim)
            metadata = []
            logger.info("Created a new FAISS index.")
        return index, metadata
    
    
    
    def add_papers(self, title:str, content: str):
        logger.info(f"Adding paper: {title}")

        chunks = self.embedding_service.chunk_document(content)

        embeddings = self.embedding_service.get_embeddings(chunks)

        embeddings= np.asarray(embeddings, dtype=np.float32)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)



        for i, chunk in enumerate(chunks):
            meta = {
                "title": title,
                "chunk_id": i,
                "content": chunk
            }
            # self.index.add(embeddings.astype(np.float32))
            self.index.add(np.array([embeddings[i]], dtype=np.float32)) #type: ignore
            self.metadata.append(meta)

        logger.info(f"Added {len(chunks)} chunks for paper '{title}' to FAISS index.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        if self.index.ntotal == 0:
            logger.warning("Search attempted on empty FAISS index.")
            return []

        # query_vector = self.model.encode([query], convert_to_numpy=True)
        query_vector = self.embedding_service.get_embeddings([query])
        distances, indices = self.index.search(query_vector.astype(np.float32), k=top_k) #type: ignore

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    "score": float(distances[0][i]),
                    "metadata": self.metadata[idx]
                })

        logger.info(f"Search completed. Found {len(results)} results.")

        return results

    def save_index(self):
        faiss.write_index(
            self.index,
            self.index_path
        )

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(
                self.metadata,
                f,
                ensure_ascii=False,
                indent=2
            )

            logger.info("FAISS index and metadata saved successfully.")
    
    def delete_index(self):
        pass



# if __name__ ==  "__main__":
#     store = VectorStore()


#     text = """
#     Artificial neural networks (ANNs) are computing systems inspired by the biological neural networks.
#     These systems learn from data, making them capable of pattern recognition and decision making.
#     """
#     store.add_papers("Neural Networks Overview", text)
#     store.save_index()

#     results = store.search("what are neural networks")
#     print(f"answer: {results}" )