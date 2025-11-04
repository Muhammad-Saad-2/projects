#type: ignore 

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from app.utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"


class PaperFetcher:
    """
    Service to fetch research papers from ArXiv API.
    """

    def __init__(self):
        logger.info("PaperFetcher initialized — ready to fetch papers from ArXiv.")

    def fetch_papers(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Fetches papers from ArXiv based on user query.

        Args:
            query (str): Search keywords (e.g., 'neural networks', 'quantum computing')
            max_results (int): Number of results to fetch

        Returns:
            List[Dict]: List of papers with metadata
        """
        logger.info(f"Fetching papers for query: '{query}' (max_results={max_results})")

        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results
        }

        try:
            response = requests.get(ARXIV_API_URL, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch from ArXiv: {e}")
            return []

        # Parse the XML feed
        root = ET.fromstring(response.text)
        papers = []

        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            paper = {
                "title": entry.find("{http://www.w3.org/2005/Atom}title").text.strip(),
                "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text.strip(),
                "authors": [author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")],
                "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
                "link": entry.find("{http://www.w3.org/2005/Atom}id").text
            }
            papers.append(paper)

        logger.info(f"Fetched {len(papers)} papers successfully from ArXiv.")
        return papers


if __name__ == "__main__":
    fetcher = PaperFetcher()
    results = fetcher.fetch_papers("nuclear fissions ", max_results=3)

    for idx, paper in enumerate(results, 1):
        print(f"\n📘 Paper {idx}: {paper['title']}")
        print(f"🧠 Authors: {', '.join(paper['authors'])}")
        print(f"📅 Published: {paper['published']}")
        print(f"🔗 Link: {paper['link']}")
        print(f"📝 Summary: {paper['summary'][:200]}...")
