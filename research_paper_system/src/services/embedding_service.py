import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        try:
            logger.info("Loading SPECTER2 embedding model...")
            _model = SentenceTransformer("allenai/specter2")
            logger.info("SPECTER2 model loaded.")
        except Exception:
            logger.warning("SPECTER2 unavailable, falling back to all-MiniLM-L6-v2")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> np.ndarray:
    model = _get_model()
    embedding = model.encode([text], normalize_embeddings=True)
    return embedding[0]


def embed_texts(texts: List[str], batch_size: int = 32) -> np.ndarray:
    model = _get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=batch_size, show_progress_bar=False)
    return np.array(embeddings)


def embed_paper(title: str, abstract: Optional[str] = None) -> np.ndarray:
    text = title
    if abstract:
        text = f"{title} {abstract}"
    return embed_text(text)


def embed_query(query: str) -> np.ndarray:
    return embed_text(query)
