import logging
from typing import Type
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.models.paper import Author, Paper, PaperSource
from src.utils.rate_limiter import rate_limiter
from src.utils.text_processing import clean_text

logger = logging.getLogger(__name__)

BASE_URL = "https://dblp.org/search/publ/api"


class DBLPSearchInput(BaseModel):
    query: str = Field(..., description="Search query for DBLP CS papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class DBLPSearchTool(BaseTool):
    name: str = "dblp_search"
    description: str = (
        "Search DBLP for computer science research papers and publications. "
        "Free, no key needed. Great for CS conferences and journals."
    )
    args_schema: Type[BaseModel] = DBLPSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on DBLP for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   Venue: {p.journal_name or p.conference_name or 'N/A'}\n"
                    f"   DOI: {p.doi or 'N/A'}"
                )
            return f"Found {len(papers)} papers on DBLP:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"DBLP search error: {e}")
            return f"Error searching DBLP: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        rate_limiter.wait("dblp", 1.0)
        params = {
            "q": query,
            "format": "json",
            "h": min(max_results, 50),
        }
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        result = data.get("result", {})
        hits = result.get("hits", {}).get("hit", [])
        for hit in hits:
            info = hit.get("info", {})
            # Authors can be a string or a list
            authors_raw = info.get("authors", {}).get("author", [])
            if isinstance(authors_raw, str):
                authors_raw = [{"text": authors_raw}]
            elif isinstance(authors_raw, dict):
                authors_raw = [authors_raw]
            authors = [Author(name=a.get("text", a) if isinstance(a, dict) else str(a)) for a in authors_raw]

            year = None
            if info.get("year"):
                try:
                    year = int(info["year"])
                except ValueError:
                    pass

            venue = info.get("venue", "")

            paper = Paper(
                title=clean_text(info.get("title", "")),
                authors=authors,
                year=year,
                source=PaperSource.DBLP,
                doi=info.get("doi"),
                url=info.get("ee", info.get("url", "")),
                journal_name=venue if "journal" in info.get("type", "").lower() else None,
                conference_name=venue if "conference" in info.get("type", "").lower() or "proceedings" in info.get("type", "").lower() else None,
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        return self._fetch_papers(query, max_results)
