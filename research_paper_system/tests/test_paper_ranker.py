import pytest
from unittest.mock import patch, MagicMock
from src.services.paper_ranker import PaperRanker
from src.models.paper import Paper, PaperSource


def test_ranker_empty_list():
    ranker = PaperRanker()
    result = ranker.rank([], "test topic")
    assert result == []


def test_ranker_single_paper():
    ranker = PaperRanker()
    papers = [
        Paper(
            title="Test Paper",
            abstract="Deep learning for healthcare",
            source=PaperSource.ARXIV,
            year=2024,
            citations_count=50,
        )
    ]
    rankings = ranker.rank(papers, "deep learning healthcare")
    assert len(rankings) == 1
    assert rankings[0].rank_position == 1
    assert 0 <= rankings[0].overall_score <= 1


def test_ranker_ordering():
    ranker = PaperRanker()
    papers = [
        Paper(title="Low cited", source=PaperSource.ARXIV, year=2020, citations_count=5),
        Paper(title="High cited", source=PaperSource.ARXIV, year=2024, citations_count=500),
    ]
    rankings = ranker.rank(papers, "test")
    assert rankings[0].overall_score >= rankings[1].overall_score
