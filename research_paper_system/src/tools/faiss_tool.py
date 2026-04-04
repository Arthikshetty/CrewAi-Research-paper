import logging
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SemanticSearchInput(BaseModel):
    query: str = Field(..., description="Search query to find semantically similar papers")
    top_k: int = Field(default=10, description="Number of similar papers to return")


class SemanticSearchTool(BaseTool):
    name: str = "semantic_search"
    description: str = (
        "Search for semantically similar research papers using FAISS vector similarity. "
        "Finds papers with related content even if they don't share exact keywords."
    )
    args_schema: Type[BaseModel] = SemanticSearchInput
    _vector_store: object = None

    def set_vector_store(self, vector_store):
        self._vector_store = vector_store

    def _run(self, query: str, top_k: int = 10) -> str:
        if not self._vector_store:
            return "Vector store not initialized. Papers need to be indexed first."
        try:
            results = self._vector_store.search(query, top_k)
            if not results:
                return "No semantically similar papers found."
            result_lines = []
            for i, (paper, score) in enumerate(results, 1):
                result_lines.append(
                    f"{i}. [Score: {score:.3f}] {paper.title}\n"
                    f"   Year: {paper.year} | Citations: {paper.citations_count}"
                )
            return f"Found {len(results)} similar papers:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return f"Error in semantic search: {e}"


class FindRelatedInput(BaseModel):
    paper_title: str = Field(..., description="Title of the paper to find related work for")
    top_k: int = Field(default=5, description="Number of related papers to return")


class FindRelatedTool(BaseTool):
    name: str = "find_related"
    description: str = (
        "Given a paper title, find the most related papers using vector similarity."
    )
    args_schema: Type[BaseModel] = FindRelatedInput
    _vector_store: object = None

    def set_vector_store(self, vector_store):
        self._vector_store = vector_store

    def _run(self, paper_title: str, top_k: int = 5) -> str:
        if not self._vector_store:
            return "Vector store not initialized."
        try:
            results = self._vector_store.search(paper_title, top_k + 1)
            # Filter out the paper itself
            filtered = [(p, s) for p, s in results if p.title.lower() != paper_title.lower()][:top_k]
            if not filtered:
                return "No related papers found."
            result_lines = []
            for i, (paper, score) in enumerate(filtered, 1):
                result_lines.append(
                    f"{i}. [Score: {score:.3f}] {paper.title}\n"
                    f"   Year: {paper.year} | Citations: {paper.citations_count}"
                )
            return f"Related papers:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"Find related error: {e}")
            return f"Error finding related papers: {e}"
