import logging
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CitationNetworkInput(BaseModel):
    paper_title: str = Field(..., description="Title of the paper to get citation network for")
    depth: int = Field(default=2, description="Depth of citation traversal")


class CitationNetworkTool(BaseTool):
    name: str = "citation_network"
    description: str = (
        "Fetch the citation subgraph for a paper from the Neo4j knowledge graph. "
        "Shows which papers cite it and which papers it references."
    )
    args_schema: Type[BaseModel] = CitationNetworkInput
    _graph_service: object = None

    def set_graph_service(self, graph_service):
        self._graph_service = graph_service

    def _run(self, paper_title: str, depth: int = 2) -> str:
        if not self._graph_service:
            return "Graph service not initialized."
        try:
            network = self._graph_service.get_citation_network(paper_title, depth)
            return str(network)
        except Exception as e:
            logger.error(f"Citation network error: {e}")
            return f"Error fetching citation network: {e}"


class BestBasePaperInput(BaseModel):
    topic: str = Field(..., description="Research topic to find the best base paper for")
    limit: int = Field(default=5, description="Number of top base papers to return")


class BestBasePaperTool(BaseTool):
    name: str = "best_base_paper"
    description: str = (
        "Find the most-referenced foundational 'base paper' using PageRank and "
        "in-degree analysis on the citation graph. Returns the paper that other "
        "discovered papers cite the most — the foundation of the research area."
    )
    args_schema: Type[BaseModel] = BestBasePaperInput
    _graph_service: object = None

    def set_graph_service(self, graph_service):
        self._graph_service = graph_service

    def _run(self, topic: str, limit: int = 5) -> str:
        if not self._graph_service:
            return "Graph service not initialized."
        try:
            results = self._graph_service.find_best_base_paper(limit)
            if not results:
                return "No base papers identified in the citation network."
            result_lines = []
            for i, bp in enumerate(results, 1):
                result_lines.append(
                    f"{i}. {bp.title}\n"
                    f"   In-degree (cited by discovered papers): {bp.total_incoming_citations}\n"
                    f"   Global citations: {bp.total_global_citations}\n"
                    f"   PageRank score: {bp.pagerank_score:.4f}\n"
                    f"   Year: {bp.year}\n"
                    f"   Referenced by: {', '.join(bp.referenced_by[:5])}"
                )
            return f"Top {len(results)} base papers:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"Best base paper error: {e}")
            return f"Error finding best base paper: {e}"


class TopAuthorsInput(BaseModel):
    topic: str = Field(..., description="Research topic to find top authors for")
    limit: int = Field(default=10, description="Number of top authors to return")


class TopAuthorsTool(BaseTool):
    name: str = "top_authors"
    description: str = (
        "Find the authors who have published the most research papers on a given topic. "
        "Returns author profiles with paper count, citations, h-index, and expertise."
    )
    args_schema: Type[BaseModel] = TopAuthorsInput
    _graph_service: object = None

    def set_graph_service(self, graph_service):
        self._graph_service = graph_service

    def _run(self, topic: str, limit: int = 10) -> str:
        if not self._graph_service:
            return "Graph service not initialized."
        try:
            results = self._graph_service.find_top_authors(limit)
            if not results:
                return "No author data available in the knowledge graph."
            result_lines = []
            for i, author in enumerate(results, 1):
                result_lines.append(
                    f"{i}. {author.author_name}\n"
                    f"   Papers on topic: {author.total_papers_on_topic}\n"
                    f"   Total citations: {author.total_citations}\n"
                    f"   h-index: {author.h_index or 'N/A'}\n"
                    f"   Active: {author.year_range_active}\n"
                    f"   Affiliations: {', '.join(author.affiliations[:3]) or 'N/A'}"
                )
            return f"Top {len(results)} authors:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"Top authors error: {e}")
            return f"Error finding top authors: {e}"


class TopicTrendInput(BaseModel):
    topic: str = Field(..., description="Research topic to analyze trends for")


class TopicTrendTool(BaseTool):
    name: str = "topic_trend"
    description: str = (
        "Get publication trend data for a topic — papers published per year, "
        "showing how research activity has changed over time."
    )
    args_schema: Type[BaseModel] = TopicTrendInput
    _graph_service: object = None

    def set_graph_service(self, graph_service):
        self._graph_service = graph_service

    def _run(self, topic: str) -> str:
        if not self._graph_service:
            return "Graph service not initialized."
        try:
            trends = self._graph_service.get_publication_trends()
            if not trends:
                return "No trend data available."
            result_lines = []
            for entry in trends:
                bar = "█" * min(entry["count"], 50)
                result_lines.append(f"  {entry['year']}: {bar} ({entry['count']} papers)")
            return f"Publication trends:\n\n" + "\n".join(result_lines)
        except Exception as e:
            logger.error(f"Topic trend error: {e}")
            return f"Error getting topic trends: {e}"


class AuthorNetworkInput(BaseModel):
    author_name: str = Field(..., description="Author name to get collaboration network for")


class AuthorNetworkTool(BaseTool):
    name: str = "author_network"
    description: str = (
        "Get the co-authorship collaboration network for a given author."
    )
    args_schema: Type[BaseModel] = AuthorNetworkInput
    _graph_service: object = None

    def set_graph_service(self, graph_service):
        self._graph_service = graph_service

    def _run(self, author_name: str) -> str:
        if not self._graph_service:
            return "Graph service not initialized."
        try:
            network = self._graph_service.get_author_network(author_name)
            return str(network)
        except Exception as e:
            logger.error(f"Author network error: {e}")
            return f"Error getting author network: {e}"
