import logging
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.models.paper import Author, Paper, PaperSource
from src.utils.rate_limiter import rate_limiter
from src.utils.text_processing import clean_text

logger = logging.getLogger(__name__)


class GoogleScholarSearchInput(BaseModel):
    query: str = Field(..., description="Search query for Google Scholar papers")
    max_results: int = Field(default=10, description="Maximum number of results (limited)")


class GoogleScholarSearchTool(BaseTool):
    name: str = "google_scholar_search"
    description: str = (
        "Search Google Scholar for research papers using the scholarly library. "
        "Broad coverage but rate-limited. Use sparingly."
    )
    args_schema: Type[BaseModel] = GoogleScholarSearchInput

    def _run(self, query: str, max_results: int = 10) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on Google Scholar (may be rate-limited)."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   Citations: {p.citations_count}\n"
                    f"   URL: {p.url or 'N/A'}"
                )
            return f"Found {len(papers)} papers on Google Scholar:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"Google Scholar search error: {e}")
            return f"Error searching Google Scholar: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        try:
            from scholarly import scholarly
        except ImportError:
            logger.error("scholarly not installed. Install with: pip install scholarly")
            return []

        rate_limiter.wait("google_scholar", 5.0)

        papers = []
        try:
            search_query = scholarly.search_pubs(query)
            for _ in range(min(max_results, 10)):
                try:
                    result = next(search_query)
                except StopIteration:
                    break

                bib = result.get("bib", {})
                authors = [Author(name=a) for a in bib.get("author", [])]

                year = None
                if bib.get("pub_year"):
                    try:
                        year = int(bib["pub_year"])
                    except ValueError:
                        pass

                paper = Paper(
                    title=clean_text(bib.get("title", "")),
                    abstract=clean_text(bib.get("abstract", "")),
                    authors=authors,
                    year=year,
                    source=PaperSource.GOOGLE_SCHOLAR,
                    url=result.get("pub_url") or result.get("eprint_url", ""),
                    pdf_url=result.get("eprint_url"),
                    citations_count=result.get("num_citations", 0),
                    journal_name=bib.get("venue"),
                )
                papers.append(paper)
                rate_limiter.wait("google_scholar", 5.0)
        except Exception as e:
            logger.warning(f"Google Scholar scraping interrupted: {e}")

        return papers

    def fetch_papers(self, query: str, max_results: int = 10) -> list[Paper]:
        return self._fetch_papers(query, max_results)
