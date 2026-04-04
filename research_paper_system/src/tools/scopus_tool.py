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

BASE_URL = "https://api.elsevier.com/content/search/scopus"


class ScopusSearchInput(BaseModel):
    query: str = Field(..., description="Search query for Scopus papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class ScopusSearchTool(BaseTool):
    name: str = "scopus_search"
    description: str = (
        "Search Scopus for multidisciplinary research papers. "
        "Returns citation metrics, author data, and metadata from Elsevier's database."
    )
    args_schema: Type[BaseModel] = ScopusSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        api_key = os.getenv("ELSEVIER_API_KEY", "")
        if not api_key:
            return "Scopus search skipped: no Elsevier API key configured."
        try:
            papers = self._fetch_papers(query, max_results, api_key)
            if not papers:
                return "No papers found on Scopus for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   Citations: {p.citations_count}\n"
                    f"   DOI: {p.doi or 'N/A'}"
                )
            return f"Found {len(papers)} papers on Scopus:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"Scopus search error: {e}")
            return f"Error searching Scopus: {e}"

    def _fetch_papers(self, query: str, max_results: int, api_key: str) -> list[Paper]:
        rate_limiter.wait("scopus", 1.0)
        headers = {
            "X-ELS-APIKey": api_key,
            "Accept": "application/json",
        }
        params = {
            "query": f"TITLE-ABS-KEY({query})",
            "count": min(max_results, 25),
            "sort": "-citedby-count",
        }
        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        results = data.get("search-results", {}).get("entry", [])
        for item in results:
            if item.get("error"):
                continue
            author_name = item.get("dc:creator", "Unknown")
            year = None
            cover_date = item.get("prism:coverDate", "")
            if cover_date:
                year = int(cover_date[:4])

            paper = Paper(
                title=clean_text(item.get("dc:title", "")),
                abstract=clean_text(item.get("dc:description", "")),
                authors=[Author(name=author_name)],
                year=year,
                source=PaperSource.SCOPUS,
                doi=item.get("prism:doi"),
                url=item.get("prism:url", ""),
                citations_count=int(item.get("citedby-count", 0)),
                journal_name=item.get("prism:publicationName"),
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        api_key = os.getenv("ELSEVIER_API_KEY", "")
        if not api_key:
            return []
        return self._fetch_papers(query, max_results, api_key)
