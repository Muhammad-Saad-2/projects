from typing import Dict, Any, List
from app.core.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore
from app.services.paper_fetcher import PaperFetcher  #type: ignore 
from app.utils.text_cleaner import clean_text, chunk_text
from app.utils.logger import get_logger
from app.services.summarizer import Summarizer  

logger = get_logger(__name__)


class RAGService:
    """
    Orchestrates the RAG (Retrieval-Augmented Generation) pipeline:
    1️⃣ Query local FAISS index
    2️⃣ If not found → Fetch from Arxiv
    3️⃣ Clean + chunk text
    4️⃣ Embed + add to vector store
    5️⃣ Summarize retrieved content using Gemini
    """

    def __init__(self):
        self.embedding_service = EmbeddingService(model_name="all-MiniLM-L6-v2")
        self.vector_store = VectorStore(embedding_dem=384, embedding_service=self.embedding_service)
        self.fetcher = PaperFetcher()
        self.summarizer = Summarizer()  # ✅ Initialize Gemini-based summarizer

        logger.info("RAGService initialized successfully.")

    def _filter_results(
        self, results: List[Dict[str, Any]], similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Filters FAISS results by similarity score threshold.
        """
        filtered = []
        for r in results:
            try:
                distance = float(r["score"])
                similarity = 1 / (1 + distance)
                if similarity >= similarity_threshold:
                    r["similarity"] = str(round(similarity, 3))
                    filtered.append(r)
            except (KeyError, ValueError):
                continue
        return filtered

    def _summarize_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Extracts text content from search results and generates a summary via Gemini.
        """
        if not results:
            return "No relevant context available for summarization."

        # Try to extract content field from metadata safely
        context_chunks = []
        for r in results:
            metadata = r.get("metadata", {})
            chunk_text = metadata.get("chunk", {}).get("text")
            if chunk_text:
                context_chunks.append(chunk_text)

        if not context_chunks:
            return "No textual content found in retrieved results."

        return self.summarizer.summarize(query, context_chunks)

    def query_knowledge(
        self, query: str, similarity_threshold: float = 0.4, top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Checks local knowledge base first, then fetches from Arxiv if not found.
        Finally, summarizes the most relevant findings.
        """
        logger.info(f"🔍 Searching vector database for query: '{query}'")
        results = self.vector_store.search(query, top_k=top_k)
        filtered_results = self._filter_results(results, similarity_threshold)

        # 🧠 Local vector store results found
        if filtered_results:
            logger.info(f"✅ Found {len(filtered_results)} results locally.")
            summary = self._summarize_results(query, filtered_results)
            return {
                "status": "success",
                "source": "local knowledge base",
                "results": filtered_results,
                "summary": summary,
            }

        #  Fallback: Fetch from Arxiv if local data is insufficient
        logger.warning("⚠️ No local results found. Triggering fallback to Arxiv.")
        fetched_papers = self.fetcher.fetch_papers(query, max_results=3)

        if not fetched_papers:
            logger.error("❌ No papers found on Arxiv.")
            return {"status": "error", 
                    "message": "No papers found for your query.",
                    "summary": "no context found for the summary",
                    "results": []
                }

        # Process and store new papers
        for paper in fetched_papers:
            cleaned_text = clean_text(paper["summary"])
            chunks = chunk_text(cleaned_text, source=paper["title"])
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_service.get_embeddings(chunk_texts)

            for i, chunk in enumerate(chunks):
                metadata = {
                    "title": paper["title"],
                    "chunk_id": i,
                    "source": "arxiv",
                    "url": paper["link"],
                    "chunk": chunk,
                }
                self.vector_store.index.add(embeddings[i].reshape(1, -1))  # type: ignore
                self.vector_store.metadata.append(metadata)

        self.vector_store.save_index()
        logger.info("🧠 Added new papers to local vector store.")

        # 🔁 Re-run the search on updated index
        updated_results = self.vector_store.search(query, top_k=top_k)
        filtered_updated_results = self._filter_results(
            updated_results, similarity_threshold
        )

        if filtered_updated_results:
            logger.info(
                f"✅ Found {len(filtered_updated_results)} new relevant results after adding Arxiv papers."
            )
            summary = self._summarize_results(query, filtered_updated_results)
            return {
                "status": "success",
                "source": "arxiv (newly added)",
                "results": filtered_updated_results,
                "summary": summary,
                "message": "No local data found — papers fetched from Arxiv and added to vector store.",
            }

        # If still nothing relevant found
        return {
            "status": "success",
            "source": "arxiv (newly added)",
            "summary": "No conclusive information found in retrieved sources.",
            "results":[],
            "message": "No local data found — papers fetched from Arxiv and added to vector store, but none met the similarity threshold.",
        }


if __name__ == "__main__":
    rag = RAGService()
    result = rag.query_knowledge("blockchain", similarity_threshold=0.5, top_k=3)
    print(result)
