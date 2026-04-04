import logging
from typing import Type
import feedparser
import urllib.parse
import urllib.request
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.models.paper import Author, Paper, PaperSource
from src.utils.rate_limiter import rate_limiter
from src.utils.text_processing import clean_text

logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"


class ArxivSearchInput(BaseModel):
    query: str = Field(..., description="Search query for ArXiv papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class ArxivSearchTool(BaseTool):
    name: str = "arxiv_search"
    description: str = (
        "Search ArXiv for research papers by keyword, title, or author. "
        "Returns paper metadata including title, abstract, authors, and PDF links."
    )
    args_schema: Type[BaseModel] = ArxivSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on ArXiv for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   ArXiv ID: {p.arxiv_id}\n"
                    f"   URL: {p.url}\n"
                    f"   Abstract: {(p.abstract or '')[:300]}..."
                )
            return f"Found {len(papers)} papers on ArXiv:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"ArXiv search error: {e}")
            return f"Error searching ArXiv: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        rate_limiter.wait("arxiv", 3.0)

        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": min(max_results, 50),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
        response = urllib.request.urlopen(url, timeout=30)
        feed = feedparser.parse(response.read())

        papers = []
        for entry in feed.entries:
            arxiv_id = entry.get("id", "").split("/abs/")[-1]
            authors = [
                Author(name=a.get("name", "Unknown"))
                for a in entry.get("authors", [])
            ]
            year = None
            if hasattr(entry, "published"):
                year = int(entry.published[:4])

            pdf_url = None
            for link in entry.get("links", []):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href")
                    break

            paper = Paper(
                title=clean_text(entry.get("title", "")),
                abstract=clean_text(entry.get("summary", "")),
                authors=authors,
                year=year,
                source=PaperSource.ARXIV,
                arxiv_id=arxiv_id,
                url=entry.get("id", ""),
                pdf_url=pdf_url or f"https://arxiv.org/pdf/{arxiv_id}",
                open_access=True,
                keywords=[t.get("term", "") for t in entry.get("tags", [])],
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        """Public method for direct access to paper objects."""
        return self._fetch_papers(query, max_results)
