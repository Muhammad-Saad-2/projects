# app/services/summarizer.py
from typing import List
from app.core.llm import GeminiLLM
from app.utils.logger import get_logger

logger = get_logger(__name__)

class Summarizer:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Wrapper service that prepares a prompt from retrieved context chunks
        and asks the Gemini LLM to produce a concise, research-oriented summary.
        """
        try:
            self.llm = GeminiLLM(model_name=model_name)
            logger.info("Summarizer initialized with GeminiLLM.")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiLLM: {e}")
            raise

    def build_prompt(self, query: str, context_chunks: List[str]) -> str:
        """
        Build a clear, focused prompt for summarization.
        We include only a bounded number of chunks to avoid exceeding context length.
        """
        # Limit context length — adjust number_of_chunks if needed
        number_of_chunks = min(len(context_chunks), 6)
        context = "\n\n---\n\n".join(context_chunks[:number_of_chunks])

        prompt = f"""
You are an expert research assistant. Given the user's research question and the retrieved
paper fragments below, produce a concise, precise, and factual summary focused only on the user's query.

User question:
{query}

Retrieved context (only relevant fragments shown):
{context}

Deliverable:
1) A short summary (3-6 sentences) answering the user's question.
2) A bullet list of up to 3 key insights or findings (each 1 line).
3) A short "sources" line listing titles or links included in the context (if available).

Be factual. Do not hallucinate. If the context doesn't contain an answer, say: "No conclusive information found in retrieved sources."
"""
        return prompt

    def summarize(self, query: str, context_chunks: List[str]) -> str:
        """
        Synchronously generate a summary via Gemini.
        Returns the LLM text (trimmed).
        """
        if not context_chunks:
            logger.warning("No context provided to summarizer.")
            return "No relevant information found to summarize."

        prompt = self.build_prompt(query, context_chunks)
        logger.info("Sending summarization prompt to Gemini.")
        try:
            summary = self.llm.generate_text(prompt)
            logger.info("Summary generated successfully.")
            return summary.strip()
        except Exception as e:
            logger.error(f"Error from GeminiLLM.generate_text: {e}")
            return "An error occurred while generating the summary."
