"""Integration test — runs a small-scale pipeline with 2 free sources (ArXiv + CrossRef).

This test verifies the end-to-end flow without paid API keys or Neo4j.
Run with:  pytest tests/test_integration.py -v -s
"""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools.arxiv_tool import ArxivSearchTool
from src.tools.crossref_tool import CrossRefSearchTool
from src.utils.deduplicator import deduplicator
from src.services.paper_ranker import PaperRanker
from src.services.vector_store import VectorStore


TOPIC = "federated learning"
MAX_PER_SOURCE = 5  # keep it small for CI


@pytest.fixture(scope="module")
def papers():
    """Fetch a handful of papers from free sources."""
    arxiv = ArxivSearchTool()
    crossref = CrossRefSearchTool()

    all_papers = []
    for tool in [arxiv, crossref]:
        try:
            all_papers.extend(tool.fetch_papers(TOPIC, MAX_PER_SOURCE))
        except Exception as exc:
            pytest.skip(f"Source unavailable: {exc}")

    if not all_papers:
        pytest.skip("No papers fetched — network may be down")

    return deduplicator.deduplicate(all_papers)


def test_papers_fetched(papers):
    assert len(papers) >= 2, f"Expected ≥2 unique papers, got {len(papers)}"


def test_papers_have_required_fields(papers):
    for p in papers:
        assert p.title, "Paper missing title"
        assert p.source, "Paper missing source"
        assert p.id, "Paper missing id"


def test_ranking(papers):
    ranker = PaperRanker()
    rankings = ranker.rank(papers, query=TOPIC)
    assert len(rankings) == len(papers)
    assert rankings[0].rank_position == 1
    assert rankings[0].overall_score >= rankings[-1].overall_score


def test_vector_store(papers):
    vs = VectorStore()
    vs.build_index(papers)
    results = vs.search(TOPIC, top_k=3)
    assert len(results) >= 1, "Vector search returned no results"
    paper, score = results[0]
    assert paper.title
    assert score > 0


def test_deduplication(papers):
    # Duplicate every paper and ensure dedup works
    doubled = papers + papers
    unique = deduplicator.deduplicate(doubled)
    assert len(unique) == len(papers)


def test_serialization(papers):
    """All papers serialize to valid JSON (needed for dashboard)."""
    for p in papers:
        data = p.model_dump()
        raw = json.dumps(data, default=str)
        assert raw  # non-empty
