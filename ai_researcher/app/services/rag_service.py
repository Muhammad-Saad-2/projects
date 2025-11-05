#type: ignore 
from typing import Dict, Any, List
from app.core.embedding_service  import EmbeddingService
from app.core.vector_store import VectorStore
from app.services.paper_fetcher import PaperFetcher #type: ignore 
from app.utils.text_cleaner import clean_text, chunk_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGService:
    """
    Orchestrates the RAG (Retrieval-Augmented Generation) pipeline:
    1️⃣ Query local FAISS index
    2️⃣ If not found → Fetch from Arxiv
    3️⃣ Clean + chunk textfor
    4️⃣ Embed + add to vector store
    5️⃣ Return top results
    """

    def __init__(self):
        self.embedding_service = EmbeddingService(model_name="all-MiniLM-L6-v2")
        self.vector_store = VectorStore(embedding_dem=384)
        self.fetcher = PaperFetcher()

        logger.info("RAGService initialized successfully.")

    def query_knowledge(self, query: str, similarity_threshold: float = 0.75, top_k: int = 3) -> Dict[str, Any]:
        """
        Checks local knowledge base first, then fetches from Arxiv if not found.
        """
        logger.info(f"🔍 Searching vector database for query: '{query}'")
        results = self.vector_store.search(query, top_k=top_k)
        
        if results:
            logger.info(f"found len{results} relevant results for your query: '{query}' from the database")

            final_results = []


            for r in results:

                # FAISS returns L2 distance — convert it into similarity (approximate)
                distance = float(r["score"])  #Force converting it into float because the distance value from json is being returned as a string
                similarity = 1 / (1 + distance)  # lower distance = higher similarity
                if similarity >= similarity_threshold:
                    r["similarity"] = str(round(similarity, 3))
                    final_results.append(r)

            if final_results:
                logger.info(f"len{final_results} passed the similarity threshold: {similarity_threshold}")

                return{
                    "status":"success",
                    "source":"local knowledge base",
                    "results": final_results
                }

        
            logger.warning("⚠️ No local results found. Triggering fallback to Arxiv.")

            fetched_papers = self.fetcher.fetch_papers(query, max_results=3)

            if not fetched_papers:
                logger.warning(f"No releavant papers found for your search")
                return{
                    "status":False,
                    "source":"Arxiv",
                    "message":"No relevant data found locally nor on Arxiv",
                    "result": []
                }
            
            logger.info(f"found len{fetched_papers} papers from Arxiv. indexing ...... ")


            
            newly_indexed_count = 0
            for paper in fetched_papers:
                cleaned_text = clean_text(paper['summary'])
                chunks = chunk_text(cleaned_text, source = paper["title"])
                chunk_texts = [chunk["text"] for chunk in chunks]

                embeddings = self.embedding_service.get_embeddings(chunk_texts)

                for i, chunk in enumerate(chunks):
                    metadata={
                        "title":paper["title"],
                        "chunk_id": i,
                        "source": "Arxiv",
                        "url": paper["link"],
                        "text":chunk["text"]
                    }
                    self.vector_store.index.add(embeddings[i].reshape(1, -1))  #type : ignore 
                    self.vector_store.metadata.append(metadata)

                #Persist updated FAISS index + metadata
                self.vector_store.save_index()
                logger.info(f"🧠 Added {newly_indexed_count} new chunks to local vector store. Re-querying...")
            
            #Requery the updated vector store
            updated_results = self.vector_store.search("query", top_k=top_k)

            final_arxiv_results=[]

            for r in updated_results:

                distance = float(r["score"])
                similarity = 1  / (1 + distance)

                if similarity >= similarity_threshold:
                    r["similarity"] = str(round(similarity, 3))
                    final_arxiv_results.append(r)
                    
                
            return {
                "status": "success",
                "source": "arxiv (newly added)",
                "message": "No local data found — papers fetched from Arxiv and added to vector store.",
                "results": final_arxiv_results
                
            }



if __name__ == "__main__":
    rag= RAGService()

    result = rag.query_knowledge("microbiology", top_k=3)
    print(result)