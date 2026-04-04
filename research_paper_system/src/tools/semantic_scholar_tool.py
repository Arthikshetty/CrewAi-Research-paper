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

BASE_URL = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,abstract,year,authors,citationCount,referenceCount,externalIds,url,openAccessPdf,citations.title,citations.externalIds,references.title,references.externalIds,fieldsOfStudy"


class SemanticScholarSearchInput(BaseModel):
    query: str = Field(..., description="Search query for Semantic Scholar papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class SemanticScholarSearchTool(BaseTool):
    name: str = "semantic_scholar_search"
    description: str = (
        "Search Semantic Scholar for research papers. Returns detailed metadata "
        "including citation counts, references, abstracts, and author info for 214M+ papers."
    )
    args_schema: Type[BaseModel] = SemanticScholarSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on Semantic Scholar for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   Citations: {p.citations_count} | References: {p.references_count}\n"
                    f"   DOI: {p.doi or 'N/A'}\n"
                    f"   Abstract: {(p.abstract or '')[:300]}..."
                )
            return f"Found {len(papers)} papers on Semantic Scholar:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"Semantic Scholar search error: {e}")
            return f"Error searching Semantic Scholar: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        rate_limiter.wait("semantic_scholar", 1.0)

        headers = {}
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        if api_key:
            headers["x-api-key"] = api_key

        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": FIELDS,
        }
        resp = requests.get(f"{BASE_URL}/paper/search", params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for item in data.get("data", []):
            ext_ids = item.get("externalIds") or {}
            authors = [
                Author(
                    name=a.get("name", "Unknown"),
                    author_id=a.get("authorId"),
                )
                for a in item.get("authors", [])
            ]
            pdf_info = item.get("openAccessPdf") or {}
            citations = item.get("citations") or []
            references = item.get("references") or []

            cited_by_ids = []
            for c in citations:
                c_ext = (c.get("externalIds") or {})
                if c_ext.get("DOI"):
                    cited_by_ids.append(c_ext["DOI"])

            ref_ids = []
            for r in references:
                r_ext = (r.get("externalIds") or {})
                if r_ext.get("DOI"):
                    ref_ids.append(r_ext["DOI"])

            paper = Paper(
                title=clean_text(item.get("title", "")),
                abstract=clean_text(item.get("abstract") or ""),
                authors=authors,
                year=item.get("year"),
                source=PaperSource.SEMANTIC_SCHOLAR,
                doi=ext_ids.get("DOI"),
                arxiv_id=ext_ids.get("ArXiv"),
                url=item.get("url", ""),
                citations_count=item.get("citationCount", 0),
                references_count=item.get("referenceCount", 0),
                pdf_url=pdf_info.get("url"),
                open_access=bool(pdf_info.get("url")),
                keywords=item.get("fieldsOfStudy") or [],
                references=ref_ids,
                cited_by=cited_by_ids,
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        return self._fetch_papers(query, max_results)
