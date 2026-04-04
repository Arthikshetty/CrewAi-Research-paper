from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class LimitationCategory(str, Enum):
    METHODOLOGICAL = "methodological"
    DATA = "data"
    SCOPE = "scope"
    GENERALIZABILITY = "generalizability"
    REPRODUCIBILITY = "reproducibility"
    SCALABILITY = "scalability"
    OTHER = "other"


class GapType(str, Enum):
    METHODOLOGICAL = "methodological"
    TOPICAL = "topical"
    APPLICATION = "application"
    DATA = "data"
    THEORETICAL = "theoretical"


class PaperSummary(BaseModel):
    paper_id: str
    title: str
    key_contributions: List[str] = Field(default_factory=list)
    methodology: str = ""
    findings: List[str] = Field(default_factory=list)
    limitations_text: str = ""
    keywords: List[str] = Field(default_factory=list)


class PaperLimitation(BaseModel):
    paper_id: str
    title: str
    limitation_description: str
    limitation_category: LimitationCategory = LimitationCategory.OTHER
    severity: int = Field(ge=1, le=5, default=3)
    evidence_quote: str = ""


class PaperRanking(BaseModel):
    paper_id: str
    title: str
    overall_score: float = 0.0
    citation_score: float = 0.0
    recency_score: float = 0.0
    relevance_score: float = 0.0
    source_authority_score: float = 0.0
    methodology_score: float = 0.0
    rank_position: int = 0


class BasePaperResult(BaseModel):
    paper_id: str
    title: str
    total_incoming_citations: int = 0  # Within discovered set
    total_global_citations: int = 0
    pagerank_score: float = 0.0
    referenced_by: List[str] = Field(default_factory=list)  # Paper IDs that cite it
    is_foundational: bool = True
    year: Optional[int] = None
    source: str = ""
    why_base_paper: str = ""  # LLM-generated justification


class TopAuthorResult(BaseModel):
    author_name: str
    orcid: Optional[str] = None
    affiliations: List[str] = Field(default_factory=list)
    total_papers_on_topic: int = 0
    total_citations: int = 0
    h_index: Optional[int] = None
    most_cited_paper: Optional[str] = None
    recent_paper: Optional[str] = None
    year_range_active: str = ""  # e.g., "2018-2024"
    collaboration_count: int = 0
    expertise_keywords: List[str] = Field(default_factory=list)


class ResearchGap(BaseModel):
    description: str
    evidence_papers: List[str] = Field(default_factory=list)
    suggested_directions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    gap_type: GapType = GapType.TOPICAL


class ProblemStatement(BaseModel):
    title: str
    background: str = ""
    problem_description: str = ""
    objectives: List[str] = Field(default_factory=list)
    scope: str = ""
    significance: str = ""
    derived_from_gaps: List[str] = Field(default_factory=list)
    derived_from_limitations: List[str] = Field(default_factory=list)
    related_papers: List[str] = Field(default_factory=list)


class ResearchIdea(BaseModel):
    title: str
    description: str = ""
    motivation: str = ""
    related_papers: List[str] = Field(default_factory=list)
    feasibility_score: int = Field(ge=1, le=10, default=5)


class CitationAnalysisReport(BaseModel):
    best_base_paper: Optional[BasePaperResult] = None
    runner_up_base_papers: List[BasePaperResult] = Field(default_factory=list)
    top_authors: List[TopAuthorResult] = Field(default_factory=list)
    research_clusters: List[Dict] = Field(default_factory=list)
    publication_trend: List[Dict] = Field(default_factory=list)  # [{year: int, count: int}]
    collaboration_patterns: List[Dict] = Field(default_factory=list)
