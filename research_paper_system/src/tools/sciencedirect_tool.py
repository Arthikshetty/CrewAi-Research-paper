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

BASE_URL = "https://api.elsevier.com/content/search/sciencedirect"


class ScienceDirectSearchInput(BaseModel):
    query: str = Field(..., description="Search query for ScienceDirect papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class ScienceDirectSearchTool(BaseTool):
    name: str = "sciencedirect_search"
    description: str = (
        "Search ScienceDirect for full-text journal articles from Elsevier publications."
    )
    args_schema: Type[BaseModel] = ScienceDirectSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        api_key = os.getenv("ELSEVIER_API_KEY", "")
        if not api_key:
            return "ScienceDirect search skipped: no Elsevier API key configured."
        try:
            papers = self._fetch_papers(query, max_results, api_key)
            if not papers:
                return "No papers found on ScienceDirect for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   DOI: {p.doi or 'N/A'}\n"
                    f"   Journal: {p.journal_name or 'N/A'}"
                )
            return f"Found {len(papers)} papers on ScienceDirect:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"ScienceDirect search error: {e}")
            return f"Error searching ScienceDirect: {e}"

    def _fetch_papers(self, query: str, max_results: int, api_key: str) -> list[Paper]:
        rate_limiter.wait("sciencedirect", 1.0)
        headers = {
            "X-ELS-APIKey": api_key,
            "Accept": "application/json",
        }
        params = {
            "qs": query,
            "count": min(max_results, 25),
            "sort": "-date",
        }
        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        results = data.get("search-results", {}).get("entry", [])
        for item in results:
            if item.get("error"):
                continue
            authors_raw = item.get("authors", {}).get("author", [])
            authors = [Author(name=a.get("$", "Unknown")) for a in authors_raw] if authors_raw else []

            year = None
            load_date = item.get("load-date", "")
            if load_date and len(load_date) >= 4:
                year = int(load_date[:4])

            paper = Paper(
                title=clean_text(item.get("dc:title", "")),
                authors=authors,
                year=year,
                source=PaperSource.SCIENCEDIRECT,
                doi=item.get("prism:doi"),
                url=item.get("prism:url", ""),
                journal_name=item.get("prism:publicationName"),
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        api_key = os.getenv("ELSEVIER_API_KEY", "")
        if not api_key:
            return []
        return self._fetch_papers(query, max_results, api_key)
