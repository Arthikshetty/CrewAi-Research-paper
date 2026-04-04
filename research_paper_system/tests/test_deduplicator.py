import pytest
from src.utils.deduplicator import Deduplicator
from src.models.paper import Paper, PaperSource


def test_dedup_by_doi():
    dedup = Deduplicator()
    papers = [
        Paper(title="Paper A", source=PaperSource.ARXIV, doi="10.1234/abc"),
        Paper(title="Paper A Copy", source=PaperSource.CROSSREF, doi="10.1234/abc"),
    ]
    result = dedup.deduplicate(papers)
    assert len(result) == 1


def test_dedup_by_title():
    dedup = Deduplicator()
    papers = [
        Paper(title="Federated Learning in Healthcare", source=PaperSource.ARXIV),
        Paper(title="Federated Learning in Healthcare", source=PaperSource.OPENALEX),
    ]
    result = dedup.deduplicate(papers)
    assert len(result) == 1


def test_dedup_different_papers():
    dedup = Deduplicator()
    papers = [
        Paper(title="Paper A", source=PaperSource.ARXIV),
        Paper(title="Paper B", source=PaperSource.CROSSREF),
    ]
    result = dedup.deduplicate(papers)
    assert len(result) == 2
