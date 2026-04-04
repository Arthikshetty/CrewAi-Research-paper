import pytest
from src.models.paper import Paper, Author, PaperSource


def test_paper_creation():
    paper = Paper(
        title="Test Paper",
        abstract="This is a test abstract",
        year=2024,
        source=PaperSource.ARXIV,
        authors=[Author(name="John Doe")],
    )
    assert paper.title == "Test Paper"
    assert paper.source == PaperSource.ARXIV
    assert len(paper.authors) == 1


def test_paper_source_enum():
    assert PaperSource.ARXIV == "arxiv"
    assert PaperSource.SEMANTIC_SCHOLAR == "semantic_scholar"
    assert PaperSource.CROSSREF == "crossref"


def test_author_defaults():
    author = Author(name="Jane Smith")
    assert author.name == "Jane Smith"
    assert author.affiliations == []
    assert author.h_index is None
    assert author.orcid is None


def test_paper_defaults():
    paper = Paper(
        title="Minimal Paper",
        source=PaperSource.OPENALEX,
    )
    assert paper.abstract is None
    assert paper.year is None
    assert paper.citations_count == 0
    assert paper.references == []
    assert paper.cited_by == []
