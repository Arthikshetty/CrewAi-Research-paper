import re
import unicodedata
from typing import List


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        # Try to break at sentence boundary
        if end < len(text):
            last_period = text.rfind(".", start, end)
            if last_period > start + max_chars // 2:
                end = last_period + 1
        chunks.append(text[start:end].strip())
        start = end - overlap
    return chunks


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    if not text:
        return []
    # Simple keyword extraction via frequency of capitalized/long words
    words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())
    stop_words = {
        "this", "that", "with", "from", "have", "been", "were", "which", "their",
        "also", "these", "than", "into", "more", "such", "based", "using", "paper",
        "results", "method", "approach", "proposed", "however", "show", "work",
    }
    filtered = [w for w in words if w not in stop_words]
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]
