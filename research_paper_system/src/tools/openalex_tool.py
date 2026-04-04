import logging
import os
from typing import Type
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.models.paper import Author, Paper, PaperSource
from src.utils.rate_limiter import rate_limiter
from src.utils.text_processing import clean_text

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openalex.org"


class OpenAlexSearchInput(BaseModel):
    query: str = Field(..., description="Search query for OpenAlex papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class OpenAlexSearchTool(BaseTool):
    name: str = "openalex_search"
    description: str = (
        "Search OpenAlex — a free, open catalog of scholarly works (250M+ papers). "
        "Provides citation data, author info, and open access links."
    )
    args_schema: Type[BaseModel] = OpenAlexSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on OpenAlex for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   Citations: {p.citations_count}\n"
                    f"   DOI: {p.doi or 'N/A'}"
                )
            return f"Found {len(papers)} papers on OpenAlex:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"OpenAlex search error: {e}")
            return f"Error searching OpenAlex: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        rate_limiter.wait("openalex", 0.2)
        email = os.getenv("OPENALEX_EMAIL", "")
        params = {
            "search": query,
            "per_page": min(max_results, 50),
            "sort": "relevance_score:desc",
        }
        if email:
            params["mailto"] = email

        resp = requests.get(f"{BASE_URL}/works", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for item in data.get("results", []):
            authors = []
            for authorship in item.get("authorships", []):
                author_info = authorship.get("author", {})
                institutions = authorship.get("institutions", [])
                affiliations = [inst.get("display_name", "") for inst in institutions if inst.get("display_name")]
                authors.append(Author(
                    name=author_info.get("display_name", "Unknown"),
                    author_id=author_info.get("id"),
                    orcid=author_info.get("orcid"),
                    affiliations=affiliations,
                ))

            oa = item.get("open_access", {})
            best_oa = item.get("best_oa_location") or {}

            paper = Paper(
                title=clean_text(item.get("display_name", "")),
                abstract=self._reconstruct_abstract(item.get("abstract_inverted_index")),
                authors=authors,
                year=item.get("publication_year"),
                source=PaperSource.OPENALEX,
                doi=item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else None,
                url=item.get("id", ""),
                citations_count=item.get("cited_by_count", 0),
                references_count=len(item.get("referenced_works", [])),
                pdf_url=best_oa.get("pdf_url"),
                open_access=oa.get("is_oa", False),
                journal_name=(item.get("primary_location") or {}).get("source", {}).get("display_name") if item.get("primary_location") else None,
                keywords=[kw.get("display_name", "") for kw in item.get("keywords", [])],
            )
            papers.append(paper)
        return papers

    def _reconstruct_abstract(self, inverted_index: dict | None) -> str:
        if not inverted_index:
            return ""
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join(word for _, word in word_positions)

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        return self._fetch_papers(query, max_results)
