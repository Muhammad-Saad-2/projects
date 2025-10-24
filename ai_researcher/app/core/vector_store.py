# import chromadb
# from chromadb.utils import embedding_functions
# from sentence_transformers import SentenceTransformer

# local_model = SentenceTransformer('all-MiniLM-L6-v2')

# embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
#     model_name="all-MiniLM-L6-v2",
#     device= "cpu",

# )


# chroma_client = chromadb.Client()

# collection = chroma_client.create_collection(
#     name="my_collection",

#     embedding_function=embedder # type: ignore[arg-type]
# )


# collection.add(
#     ids= ["1", "2", "3"],
#     documents = [
#         "This the document about  cats",
#         "This is the docuemnt about dogs",
#         "This document is about birds"
#     ],
# )

# results = collection.query(
#     query_texts=["This is a document about felines"],
#     n_results=2
# )

# print(results)


import os 
import json
from xml.parsers.expat import model
import numpy as np
import faiss  #type: ignore
from typing import List, Tuple, Any, Dict
from embeddings import EmbeddingService


#path setup for FAISS index and metadata storga 
VECTOR_INDEX_PATH = "./app/data/vector_store/index.faiss"
METADATA_PATH = "./app/data/vector_store/metadata.json" 



class VectorStore:
    def __init__(self, embedding_dem: int = 384):
        self.embedding_dim = embedding_dem
        self.index_path = VECTOR_INDEX_PATH
        self.metadata_path = METADATA_PATH

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_service = EmbeddingService(model_name="all-MiniLM-L6-v2")
        self.index, self.metadata = self._load_or_initialize()

    
    def _load_or_initialize(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            index = faiss.IndexFlatL2(self.embedding_dim)
            metadata = []
        return index, metadata
    
    
    
    def add_papers(self, title:str, content: str):
        # chunks = self.chunk_document(content)
        
        # embeddings = self.model.encode(chunks, convert_to_numpy=True)

        chunks = self.embedding_service.chunk_document(content)

        embeddings = self.embedding_service.get_embeddings(chunks)



        for i, chunk in enumerate(chunks):
            meta = {
                "title": title,
                "chunk_id": i,
                "content": chunk
            }
            self.index.add(embeddings.astype(np.float32))
            self.metadata.append(meta)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        if self.index.ntotal == 0:
            return []

        # query_vector = self.model.encode([query], convert_to_numpy=True)
        query_vector = self.embedding_service.get_embeddings([query])
        distances, indices = self.index.search(query_vector.astype(np.float32), top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    "score": float(distances[0][i]),
                    "metadata": self.metadata[idx]
                })

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

            print("index and metadat saved succefully")



if __name__ ==  "__main__":
    store = VectorStore()


    text = """
    Artificial neural networks (ANNs) are computing systems inspired by the biological neural networks.
    These systems learn from data, making them capable of pattern recognition and decision making.
    """
    store.add_papers("Neural Networks Overview", text)

    results = store.search("what are neural networks")
    print(f"answer: {results}" )