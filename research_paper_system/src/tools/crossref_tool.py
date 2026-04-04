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

BASE_URL = "https://api.crossref.org/works"


class CrossRefSearchInput(BaseModel):
    query: str = Field(..., description="Search query for CrossRef papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class CrossRefSearchTool(BaseTool):
    name: str = "crossref_search"
    description: str = (
        "Search CrossRef for DOI-registered research papers. Free, no key needed. "
        "Access 150M+ records with citation and metadata."
    )
    args_schema: Type[BaseModel] = CrossRefSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on CrossRef for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   Citations: {p.citations_count}\n"
                    f"   DOI: {p.doi or 'N/A'}"
                )
            return f"Found {len(papers)} papers on CrossRef:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"CrossRef search error: {e}")
            return f"Error searching CrossRef: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        rate_limiter.wait("crossref", 0.1)
        email = os.getenv("OPENALEX_EMAIL", "")
        params = {
            "query": query,
            "rows": min(max_results, 50),
            "sort": "relevance",
            "order": "desc",
        }
        if email:
            params["mailto"] = email

        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for item in data.get("message", {}).get("items", []):
            title_parts = item.get("title", [])
            title = title_parts[0] if title_parts else "Untitled"

            authors = []
            for a in item.get("author", []):
                name_parts = [a.get("given", ""), a.get("family", "")]
                name = " ".join(p for p in name_parts if p).strip()
                if name:
                    authors.append(Author(
                        name=name,
                        orcid=a.get("ORCID"),
                        affiliations=[aff.get("name", "") for aff in a.get("affiliation", [])],
                    ))

            year = None
            date_parts = item.get("published", {}).get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]

            abstract = clean_text(item.get("abstract", ""))
            # CrossRef abstracts sometimes have JATS XML tags
            import re
            abstract = re.sub(r"<[^>]+>", "", abstract)

            paper = Paper(
                title=clean_text(title),
                abstract=abstract,
                authors=authors,
                year=year,
                source=PaperSource.CROSSREF,
                doi=item.get("DOI"),
                url=item.get("URL", ""),
                citations_count=item.get("is-referenced-by-count", 0),
                references_count=item.get("references-count", 0),
                journal_name=item.get("container-title", [None])[0] if item.get("container-title") else None,
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        return self._fetch_papers(query, max_results)
