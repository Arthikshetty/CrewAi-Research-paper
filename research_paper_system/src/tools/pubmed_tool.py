import logging
import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.models.paper import Author, Paper, PaperSource
from src.utils.rate_limiter import rate_limiter
from src.utils.text_processing import clean_text

logger = logging.getLogger(__name__)


class PubMedSearchInput(BaseModel):
    query: str = Field(..., description="Search query for PubMed biomedical papers")
    max_results: int = Field(default=20, description="Maximum number of results")


class PubMedSearchTool(BaseTool):
    name: str = "pubmed_search"
    description: str = (
        "Search PubMed/NCBI for biomedical and life sciences research papers. "
        "Free access to 36M+ citations and abstracts."
    )
    args_schema: Type[BaseModel] = PubMedSearchInput

    def _run(self, query: str, max_results: int = 20) -> str:
        try:
            papers = self._fetch_papers(query, max_results)
            if not papers:
                return "No papers found on PubMed for this query."
            result_lines = []
            for i, p in enumerate(papers, 1):
                authors_str = ", ".join(a.name for a in p.authors[:5])
                result_lines.append(
                    f"{i}. [{p.year}] {p.title}\n"
                    f"   Authors: {authors_str}\n"
                    f"   DOI: {p.doi or 'N/A'}\n"
                    f"   Abstract: {(p.abstract or '')[:300]}..."
                )
            return f"Found {len(papers)} papers on PubMed:\n\n" + "\n\n".join(result_lines)
        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return f"Error searching PubMed: {e}"

    def _fetch_papers(self, query: str, max_results: int) -> list[Paper]:
        rate_limiter.wait("pubmed", 0.34)

        try:
            from Bio import Entrez
        except ImportError:
            logger.error("biopython not installed. Install with: pip install biopython")
            return []

        Entrez.email = os.getenv("OPENALEX_EMAIL", "researcher@example.com")
        api_key = os.getenv("NCBI_API_KEY", "")
        if api_key:
            Entrez.api_key = api_key

        # Search for IDs
        handle = Entrez.esearch(db="pubmed", term=query, retmax=min(max_results, 50), sort="relevance")
        search_results = Entrez.read(handle)
        handle.close()
        id_list = search_results.get("IdList", [])

        if not id_list:
            return []

        # Fetch details
        rate_limiter.wait("pubmed", 0.34)
        handle = Entrez.efetch(db="pubmed", id=",".join(id_list), rettype="xml", retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        papers = []
        for article_wrapper in records.get("PubmedArticle", []):
            article = article_wrapper.get("MedlineCitation", {}).get("Article", {})
            title = str(article.get("ArticleTitle", ""))
            abstract_parts = article.get("Abstract", {}).get("AbstractText", [])
            abstract = " ".join(str(part) for part in abstract_parts)

            authors = []
            for a in article.get("AuthorList", []):
                last = a.get("LastName", "")
                first = a.get("ForeName", "")
                if last:
                    authors.append(Author(name=f"{first} {last}".strip()))

            year = None
            date_info = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
            if date_info.get("Year"):
                year = int(date_info["Year"])

            # Extract DOI
            doi = None
            article_id_list = article_wrapper.get("PubmedData", {}).get("ArticleIdList", [])
            for aid in article_id_list:
                if hasattr(aid, "attributes") and aid.attributes.get("IdType") == "doi":
                    doi = str(aid)

            journal = article.get("Journal", {}).get("Title", "")

            paper = Paper(
                title=clean_text(title),
                abstract=clean_text(abstract),
                authors=authors,
                year=year,
                source=PaperSource.PUBMED,
                doi=doi,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{id_list[len(papers)]}/",
                journal_name=journal,
            )
            papers.append(paper)
        return papers

    def fetch_papers(self, query: str, max_results: int = 20) -> list[Paper]:
        return self._fetch_papers(query, max_results)
