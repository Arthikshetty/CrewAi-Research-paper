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

BASE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"


class IEEESearchInput(BaseModel):
    query: str = Field(..., description="Search query for IEEE Xplore papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class IEEESearchTool(BaseTool):
    name: str = "ieee_search"
    description: str = (
        "Search IEEE Xplore for engineering and CS research papers. "
        "Requires IEEE API key. Returns paper metadata."
    )
    args_schema: Type[BaseModel] = IEEESearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        api_key = os.getenv("IEEE_API_KEY", "")
        if not api_key:
            return "IEEE Xplore search skipped: no API key configured."
        try:
            papers = self._fetch_papers(query, max_results, api_key)
            if not papers:
                return "No papers found on IEEE Xplore for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   DOI: {p.doi or 'N/A'}\n"
                    f"   Abstract: {(p.abstract or '')[:300]}..."
                )
            return f"Found {len(papers)} papers on IEEE Xplore:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"IEEE search error: {e}")
            return f"Error searching IEEE Xplore: {e}"

    def _fetch_papers(self, query: str, max_results: int, api_key: str) -> list[Paper]:
        rate_limiter.wait("ieee", 1.0)
        params = {
            "apikey": api_key,
            "querytext": query,
            "max_records": min(max_results, 25),
            "sort_order": "desc",
            "sort_field": "article_number",
        }
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for article in data.get("articles", []):
            authors = [
                Author(name=a.get("full_name", "Unknown"))
                for a in article.get("authors", {}).get("authors", [])
            ]
            paper = Paper(
                title=clean_text(article.get("title", "")),
                abstract=clean_text(article.get("abstract", "")),
                authors=authors,
                year=int(article.get("publication_year", 0)) or None,
                source=PaperSource.IEEE,
                doi=article.get("doi"),
                url=article.get("html_url", ""),
                pdf_url=article.get("pdf_url"),
                journal_name=article.get("publication_title"),
                conference_name=article.get("conference_name"),
                citations_count=article.get("citing_paper_count", 0),
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        api_key = os.getenv("IEEE_API_KEY", "")
        if not api_key:
            return []
        return self._fetch_papers(query, max_results, api_key)
