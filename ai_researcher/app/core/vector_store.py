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
import numpy as np
import faiss  #type: ignore


#path setup for FAISS index and metadata storga 
VECTOR_INDEX_PATH = "./app/data/vector_store/index.faiss"
METADATA_PATH = "./app/data/vector_store/metadata.json"

def initialize_faiss(embedding_dim: int):
    """
    Initializes or loads a FAISS index.

    Args:
        embedding_dim (int): Dimension of embedding vectors.

    Returns:
        index (faiss.IndexFlatL2): Loaded or newly created FAISS index.
        metadata (list): Existing or empty metadata list.
    """
    os.makedirs(os.path.dirname(VECTOR_INDEX_PATH), exist_ok=True)

    # If index exists → load it
    if os.path.exists(VECTOR_INDEX_PATH) and os.path.exists(METADATA_PATH):
        index = faiss.read_index(VECTOR_INDEX_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        print("✅ Loaded existing FAISS index with", len(metadata), "entries.")
    else:
        index = faiss.IndexFlatL2(embedding_dim)
        metadata = []
        print("🆕 Created new FAISS index.")

    return index, metadata


def add_to_index(index, metadata_list, embedding: np.ndarray, meta: dict):
    """
    Adds a new vector and its metadata to the index.

    Args:
        index: FAISS index
        metadata_list: List storing metadata entries
        embedding: np.ndarray of shape (1, embedding_dim)
        meta: dict containing paper or summary metadata
    """
    index.add(embedding.astype(np.float32))
    metadata_list.append(meta)

def search_index(index, metadata_list, query_vector: np.ndarray, top_k: int = 3):

    """
    Searches for the most similar vectors to the query.

    Args:
        index: FAISS index
        metadata_list: List of metadata entries
        query_vector: np.ndarray of shape (1, embedding_dim)
        top_k: Number of top results to retrieve

    Returns:
        list of dicts with 'score' and 'metadata'
    """
    if index.ntotal == 0:
        return []

    distances, indices = index.search(query_vector.astype(np.float32), top_k)
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata_list):
            results.append({
                "score": float(distances[0][i]),
                "metadata": metadata_list[idx]
            })
    return results



def save_index(index, metadata_list):
    """
    Saves the FAISS index and metadata to disk.
    """
    os.makedirs(os.path.dirname(VECTOR_INDEX_PATH), exist_ok=True)

    faiss.write_index(index, VECTOR_INDEX_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    print("💾 Index and metadata saved successfully.")


if __name__ == "__main__":
    dim = 384  # Example: MiniLM-L6-v2 embedding dimension

    index, metadata = initialize_faiss(dim)

    # Dummy embedding
    emb = np.random.rand(1, dim).astype(np.float32)
    add_to_index(index, metadata, emb, {"title": "Test Paper", "summary": "Sample abstract"})

    save_index(index, metadata)

    query = np.random.rand(1, dim).astype(np.float32)
    results = search_index(index, metadata, query)
    print(results)

