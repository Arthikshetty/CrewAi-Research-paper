from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class PaperSource(str, Enum):
    ARXIV = "arxiv"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    IEEE = "ieee"
    SCOPUS = "scopus"
    SCIENCEDIRECT = "sciencedirect"
    CROSSREF = "crossref"
    OPENALEX = "openalex"
    CORE = "core"
    PUBMED = "pubmed"
    DBLP = "dblp"
    GOOGLE_SCHOLAR = "google_scholar"


class Author(BaseModel):
    name: str
    affiliations: List[str] = Field(default_factory=list)
    paper_count: int = 0
    h_index: Optional[int] = None
    orcid: Optional[str] = None
    author_id: Optional[str] = None  # Source-specific ID


class Citation(BaseModel):
    source_paper_id: str
    target_paper_id: str
    context: Optional[str] = None


class Paper(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    abstract: Optional[str] = None
    authors: List[Author] = Field(default_factory=list)
    year: Optional[int] = None
    source: PaperSource
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    citations_count: int = 0
    references_count: int = 0
    pdf_url: Optional[str] = None
    journal_name: Optional[str] = None
    conference_name: Optional[str] = None
    impact_factor: Optional[float] = None
    open_access: bool = False
    full_text: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)  # List of DOIs/IDs
    cited_by: List[str] = Field(default_factory=list)
