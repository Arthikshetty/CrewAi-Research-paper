import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SourceConfig:
    name: str
    base_url: str
    api_key_env: Optional[str] = None
    rate_limit_delay: float = 1.0  # seconds between requests
    max_results_per_query: int = 20
    enabled: bool = True


# All source configurations
SOURCES = {
    "arxiv": SourceConfig(
        name="ArXiv",
        base_url="http://export.arxiv.org/api/query",
        rate_limit_delay=3.0,
        max_results_per_query=50,
    ),
    "semantic_scholar": SourceConfig(
        name="Semantic Scholar",
        base_url="https://api.semanticscholar.org/graph/v1",
        api_key_env="SEMANTIC_SCHOLAR_API_KEY",
        rate_limit_delay=1.0,
        max_results_per_query=100,
    ),
    "ieee": SourceConfig(
        name="IEEE Xplore",
        base_url="https://ieeexploreapi.ieee.org/api/v1/search/articles",
        api_key_env="IEEE_API_KEY",
        rate_limit_delay=1.0,
        max_results_per_query=25,
    ),
    "scopus": SourceConfig(
        name="Scopus",
        base_url="https://api.elsevier.com/content/search/scopus",
        api_key_env="ELSEVIER_API_KEY",
        rate_limit_delay=1.0,
        max_results_per_query=25,
    ),
    "sciencedirect": SourceConfig(
        name="ScienceDirect",
        base_url="https://api.elsevier.com/content/search/sciencedirect",
        api_key_env="ELSEVIER_API_KEY",
        rate_limit_delay=1.0,
        max_results_per_query=25,
    ),
    "crossref": SourceConfig(
        name="CrossRef",
        base_url="https://api.crossref.org/works",
        rate_limit_delay=0.1,
        max_results_per_query=50,
    ),
    "openalex": SourceConfig(
        name="OpenAlex",
        base_url="https://api.openalex.org",
        rate_limit_delay=0.2,
        max_results_per_query=50,
    ),
    "core": SourceConfig(
        name="CORE",
        base_url="https://api.core.ac.uk/v3",
        api_key_env="CORE_API_KEY",
        rate_limit_delay=2.0,
        max_results_per_query=50,
    ),
    "pubmed": SourceConfig(
        name="PubMed",
        base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        api_key_env="NCBI_API_KEY",
        rate_limit_delay=0.34,
        max_results_per_query=50,
    ),
    "dblp": SourceConfig(
        name="DBLP",
        base_url="https://dblp.org/search/publ/api",
        rate_limit_delay=1.0,
        max_results_per_query=50,
    ),
    "google_scholar": SourceConfig(
        name="Google Scholar",
        base_url="",
        api_key_env="SERPAPI_KEY",
        rate_limit_delay=5.0,
        max_results_per_query=20,
    ),
}


@dataclass
class Settings:
    # LLM
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_api_base: str = field(default_factory=lambda: os.getenv("OPENAI_API_BASE", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    llm_model_summarization: str = field(
        default_factory=lambda: os.getenv("LLM_MODEL_SUMMARIZATION", "gpt-4o")
    )

    # Neo4j
    neo4j_uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    neo4j_user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    neo4j_password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "password"))

    # Source API keys
    semantic_scholar_api_key: str = field(
        default_factory=lambda: os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    )
    ieee_api_key: str = field(default_factory=lambda: os.getenv("IEEE_API_KEY", ""))
    elsevier_api_key: str = field(default_factory=lambda: os.getenv("ELSEVIER_API_KEY", ""))
    core_api_key: str = field(default_factory=lambda: os.getenv("CORE_API_KEY", ""))
    ncbi_api_key: str = field(default_factory=lambda: os.getenv("NCBI_API_KEY", ""))
    openalex_email: str = field(default_factory=lambda: os.getenv("OPENALEX_EMAIL", ""))
    serpapi_key: str = field(default_factory=lambda: os.getenv("SERPAPI_KEY", ""))

    # FAISS
    faiss_index_dir: str = "data/faiss_index"

    # Defaults
    default_years: int = 5
    default_min_papers: int = 30
    default_num_ideas: int = 5


settings = Settings()
