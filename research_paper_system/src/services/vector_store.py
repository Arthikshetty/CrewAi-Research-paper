import logging
import numpy as np
from typing import Dict, List, Tuple
from src.models.paper import Paper
from src.services import embedding_service

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for semantic paper search. Rebuilt fresh per search."""

    def __init__(self):
        self._index = None
        self._papers: List[Paper] = []
        self._id_map: Dict[int, str] = {}  # FAISS index -> paper.id

    def build_index(self, papers: List[Paper]):
        import faiss

        self._papers = papers
        if not papers:
            return

        # Generate embeddings
        texts = [f"{p.title} {p.abstract or ''}" for p in papers]
        logger.info(f"Generating embeddings for {len(papers)} papers...")
        embeddings = embedding_service.embed_texts(texts)

        # Build FAISS index
        dimension = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dimension)  # Inner product after L2-normalization = cosine similarity
        self._index.add(embeddings.astype(np.float32))

        # Build ID mapping
        self._id_map = {i: p.id for i, p in enumerate(papers)}
        logger.info(f"FAISS index built with {self._index.ntotal} vectors (dim={dimension})")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Paper, float]]:
        if not self._index or self._index.ntotal == 0:
            return []

        query_vec = embedding_service.embed_query(query).reshape(1, -1).astype(np.float32)
        scores, indices = self._index.search(query_vec, min(top_k, self._index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            paper = self._papers[idx]
            results.append((paper, float(score)))
        return results

    @property
    def paper_count(self) -> int:
        return len(self._papers)
