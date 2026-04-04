import logging
from datetime import datetime
from typing import List
from src.models.paper import Paper
from src.models.analysis import PaperRanking

logger = logging.getLogger(__name__)

# Scoring weights
W_CITATION = 0.30
W_RECENCY = 0.20
W_RELEVANCE = 0.25
W_SOURCE = 0.15
W_METHODOLOGY = 0.10

# Source authority scores
SOURCE_SCORES = {
    "semantic_scholar": 0.8,
    "scopus": 0.9,
    "ieee": 0.85,
    "sciencedirect": 0.85,
    "crossref": 0.7,
    "openalex": 0.75,
    "pubmed": 0.85,
    "arxiv": 0.6,
    "core": 0.5,
    "dblp": 0.7,
    "google_scholar": 0.5,
}


class PaperRanker:
    """Multi-signal paper ranking engine."""

    def rank(self, papers: List[Paper], query: str = "") -> List[PaperRanking]:
        if not papers:
            return []

        max_citations = max(p.citations_count for p in papers) or 1
        current_year = datetime.now().year

        rankings = []
        for paper in papers:
            # Citation score (0-1)
            citation_score = paper.citations_count / max_citations

            # Recency score (0-1): newer is better
            if paper.year:
                age = current_year - paper.year
                recency_score = max(0, 1.0 - (age / 20.0))
            else:
                recency_score = 0.3

            # Source authority score
            source_score = SOURCE_SCORES.get(paper.source.value, 0.5)

            # Relevance score (basic: title/abstract keyword match)
            relevance_score = 0.5
            if query:
                query_lower = query.lower()
                title_lower = paper.title.lower()
                if query_lower in title_lower:
                    relevance_score = 1.0
                else:
                    words = query_lower.split()
                    matches = sum(1 for w in words if w in title_lower)
                    relevance_score = min(1.0, matches / max(len(words), 1))

            # Methodology score (proxy: has abstract + newer)
            methodology_score = 0.5
            if paper.abstract and len(paper.abstract) > 200:
                methodology_score += 0.3
            if paper.open_access:
                methodology_score += 0.2
            methodology_score = min(1.0, methodology_score)

            # Overall weighted score
            overall = (
                W_CITATION * citation_score
                + W_RECENCY * recency_score
                + W_RELEVANCE * relevance_score
                + W_SOURCE * source_score
                + W_METHODOLOGY * methodology_score
            )

            rankings.append(PaperRanking(
                paper_id=paper.id,
                title=paper.title,
                overall_score=round(overall, 4),
                citation_score=round(citation_score, 4),
                recency_score=round(recency_score, 4),
                relevance_score=round(relevance_score, 4),
                source_authority_score=round(source_score, 4),
                methodology_score=round(methodology_score, 4),
            ))

        # Sort and assign rank positions
        rankings.sort(key=lambda r: r.overall_score, reverse=True)
        for i, r in enumerate(rankings, 1):
            r.rank_position = i

        return rankings
