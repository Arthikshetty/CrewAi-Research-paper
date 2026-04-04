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

BASE_URL = "https://api.core.ac.uk/v3"


class CoreSearchInput(BaseModel):
    query: str = Field(..., description="Search query for CORE open access papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class CoreSearchTool(BaseTool):
    name: str = "core_search"
    description: str = (
        "Search CORE for open access research papers. Aggregates 381M+ papers "
        "from 15K+ providers worldwide, including full text."
    )
    args_schema: Type[BaseModel] = CoreSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on CORE for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   DOI: {p.doi or 'N/A'}"
                )
            return f"Found {len(papers)} papers on CORE:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"CORE search error: {e}")
            return f"Error searching CORE: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        rate_limiter.wait("core", 2.0)
        headers = {"Accept": "application/json"}
        api_key = os.getenv("CORE_API_KEY", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        params = {
            "q": query,
            "limit": min(max_results, 50),
        }
        resp = requests.get(f"{BASE_URL}/search/works", params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for item in data.get("results", []):
            authors = [
                Author(name=a.get("name", "Unknown"))
                for a in item.get("authors", [])
            ]
            year = None
            published_date = item.get("publishedDate") or item.get("yearPublished")
            if published_date:
                try:
                    year = int(str(published_date)[:4])
                except ValueError:
                    pass

            paper = Paper(
                title=clean_text(item.get("title", "")),
                abstract=clean_text(item.get("abstract") or ""),
                authors=authors,
                year=year,
                source=PaperSource.CORE,
                doi=item.get("doi"),
                url=item.get("downloadUrl") or item.get("sourceFulltextUrls", [""])[0] if item.get("sourceFulltextUrls") else "",
                pdf_url=item.get("downloadUrl"),
                open_access=True,
                journal_name=item.get("publisher"),
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        return self._fetch_papers(query, max_results)
