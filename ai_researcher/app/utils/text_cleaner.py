import re
from typing import List, Dict



def clean_text(text: str) -> str:
    """
    Basic cleanup for research paper text:
    - Removes excessive whitespace
    - Normalizes line breaks
    """
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
    source: str = ""
) -> List[Dict]:
    """
    Splits cleaned text into overlapping chunks for embedding.
    Returns a list of chunks, each with text, chunk_id, and source.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""
    chunk_id = 0

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "source": source
            })
            chunk_id += 1
            # Keep small overlap for context continuity
            overlap_part = current_chunk[-overlap:]
            current_chunk = overlap_part + " " + sentence

    # Add the final chunk
    if current_chunk.strip():
        chunks.append({
            "chunk_id": chunk_id,
            "text": current_chunk.strip(),
            "source": source
        })

    return chunks