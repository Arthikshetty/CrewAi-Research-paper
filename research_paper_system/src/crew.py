import logging
import os
from typing import List
import yaml
from crewai import Agent, Crew, Process, Task
from src.config.settings import settings
from src.models.paper import Paper
from src.services.graph_service import GraphService
from src.services.paper_ranker import PaperRanker
from src.services.progress_tracker import progress_tracker
from src.services.vector_store import VectorStore
from src.tools.arxiv_tool import ArxivSearchTool
from src.tools.core_tool import CoreSearchTool
from src.tools.crossref_tool import CrossRefSearchTool
from src.tools.dblp_tool import DBLPSearchTool
from src.tools.faiss_tool import FindRelatedTool, SemanticSearchTool
from src.tools.google_scholar_tool import GoogleScholarSearchTool
from src.tools.ieee_tool import IEEESearchTool
from src.tools.neo4j_tool import (
    AuthorNetworkTool,
    BestBasePaperTool,
    CitationNetworkTool,
    TopAuthorsTool,
    TopicTrendTool,
)
from src.tools.openalex_tool import OpenAlexSearchTool
from src.tools.pdf_tool import PDFExtractionTool
from src.tools.pubmed_tool import PubMedSearchTool
from src.tools.scopus_tool import ScopusSearchTool
from src.tools.sciencedirect_tool import ScienceDirectSearchTool
from src.tools.semantic_scholar_tool import SemanticScholarSearchTool
from src.utils.deduplicator import deduplicator

logger = logging.getLogger(__name__)

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def _load_yaml(filename: str) -> dict:
    path = os.path.join(CONFIG_DIR, filename)
    with open(path, "r") as f:
        return yaml.safe_load(f)


class ResearchPaperCrew:
    """Orchestrates the full research paper discovery and analysis pipeline."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.graph_service = GraphService(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
        )
        self.paper_ranker = PaperRanker()
        self.all_papers: List[Paper] = []

        # Initialize tools
        self.arxiv_tool = ArxivSearchTool()
        self.semantic_scholar_tool = SemanticScholarSearchTool()
        self.ieee_tool = IEEESearchTool()
        self.scopus_tool = ScopusSearchTool()
        self.sciencedirect_tool = ScienceDirectSearchTool()
        self.crossref_tool = CrossRefSearchTool()
        self.openalex_tool = OpenAlexSearchTool()
        self.core_tool = CoreSearchTool()
        self.pubmed_tool = PubMedSearchTool()
        self.dblp_tool = DBLPSearchTool()
        self.google_scholar_tool = GoogleScholarSearchTool()
        self.pdf_tool = PDFExtractionTool()

        # FAISS tools (need vector store injection)
        self.semantic_search_tool = SemanticSearchTool()
        self.find_related_tool = FindRelatedTool()
        self.semantic_search_tool.set_vector_store(self.vector_store)
        self.find_related_tool.set_vector_store(self.vector_store)

        # Neo4j tools (need graph service injection)
        self.citation_network_tool = CitationNetworkTool()
        self.best_base_paper_tool = BestBasePaperTool()
        self.top_authors_tool = TopAuthorsTool()
        self.topic_trend_tool = TopicTrendTool()
        self.author_network_tool = AuthorNetworkTool()

    def _inject_graph_service(self):
        self.citation_network_tool.set_graph_service(self.graph_service)
        self.best_base_paper_tool.set_graph_service(self.graph_service)
        self.top_authors_tool.set_graph_service(self.graph_service)
        self.topic_trend_tool.set_graph_service(self.graph_service)
        self.author_network_tool.set_graph_service(self.graph_service)

    def _build_agents(self) -> dict:
        agents_config = _load_yaml("agents.yaml")

        search_tools = [
            self.arxiv_tool, self.semantic_scholar_tool, self.ieee_tool,
            self.scopus_tool, self.sciencedirect_tool, self.crossref_tool,
            self.openalex_tool, self.core_tool, self.pubmed_tool,
            self.dblp_tool, self.google_scholar_tool,
        ]

        agents = {}
        for key, cfg in agents_config.items():
            tools = []
            if "search" in key:
                tools = search_tools + [self.semantic_search_tool]
            elif "summarization" in key:
                tools = [self.pdf_tool]
            elif "limitation" in key:
                tools = [self.pdf_tool]
            elif "citation" in key:
                tools = [
                    self.citation_network_tool, self.best_base_paper_tool,
                    self.top_authors_tool, self.topic_trend_tool,
                    self.author_network_tool,
                ]
            elif "gap" in key:
                tools = [self.semantic_search_tool, self.find_related_tool, self.topic_trend_tool]
            elif "problem" in key:
                tools = [self.semantic_search_tool]
            elif "idea" in key:
                tools = [self.semantic_search_tool]

            agents[key] = Agent(
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                tools=tools,
                verbose=cfg.get("verbose", True),
                allow_delegation=cfg.get("allow_delegation", False),
                llm=settings.llm_model_summarization if "summarization" in key else settings.llm_model,
            )
        return agents

    def _build_tasks(self, agents: dict, inputs: dict) -> list:
        tasks_config = _load_yaml("tasks.yaml")
        task_objects = {}
        task_order = [
            "discover_papers",
            "summarize_papers",
            "extract_limitations",
            "analyze_citations",
            "detect_gaps",
            "generate_problem_statements",
            "generate_ideas",
        ]

        for task_key in task_order:
            cfg = tasks_config[task_key]
            # Resolve agent reference
            agent_key = cfg["agent"]
            agent = agents[agent_key]

            # Format description with inputs
            description = cfg["description"].format(**inputs)
            expected_output = cfg["expected_output"]

            # Resolve context dependencies
            context = []
            for ctx_key in cfg.get("context", []):
                if ctx_key in task_objects:
                    context.append(task_objects[ctx_key])

            task = Task(
                description=description,
                expected_output=expected_output,
                agent=agent,
                context=context if context else None,
            )
            task_objects[task_key] = task

        return [task_objects[k] for k in task_order]

    def fetch_all_papers(self, topic: str, max_per_source: int = 20) -> List[Paper]:
        """Fetch papers from all sources live, deduplicate, and return."""
        all_papers = []

        source_tools = [
            ("Searching ArXiv", self.arxiv_tool),
            ("Searching Semantic Scholar", self.semantic_scholar_tool),
            ("Searching IEEE Xplore", self.ieee_tool),
            ("Searching Scopus", self.scopus_tool),
            ("Searching ScienceDirect", self.sciencedirect_tool),
            ("Searching CrossRef", self.crossref_tool),
            ("Searching OpenAlex", self.openalex_tool),
            ("Searching CORE", self.core_tool),
            ("Searching PubMed", self.pubmed_tool),
            ("Searching DBLP", self.dblp_tool),
            ("Searching Google Scholar", self.google_scholar_tool),
        ]

        for step_name, tool in source_tools:
            progress_tracker.on_step_start(step_name)
            try:
                papers = tool.fetch_papers(topic, max_per_source)
                all_papers.extend(papers)
                progress_tracker.on_step_complete(step_name, f"found {len(papers)} papers", len(papers))
            except Exception as e:
                logger.error(f"Error fetching from {step_name}: {e}")
                progress_tracker.on_step_error(step_name, str(e))

        # Deduplicate
        progress_tracker.on_step_start("Deduplicating papers")
        unique_papers = deduplicator.deduplicate(all_papers)
        progress_tracker.on_step_complete(
            "Deduplicating papers",
            f"{len(all_papers)} → {len(unique_papers)} unique",
            len(unique_papers),
        )

        self.all_papers = unique_papers
        return unique_papers

    def run(self, topic: str, years: int = 5, min_papers: int = 30, num_ideas: int = 5) -> dict:
        """Execute the full pipeline."""
        progress_tracker.reset()

        # Step 1: Fetch papers from all sources (LIVE)
        logger.info(f"Starting live paper fetch for topic: {topic}")
        papers = self.fetch_all_papers(topic, max_per_source=20)
        logger.info(f"Total unique papers: {len(papers)}")

        if not papers:
            return {"error": "No papers found for the given topic."}

        # Step 2: Rank papers
        progress_tracker.on_step_start("Ranking papers")
        rankings = self.paper_ranker.rank(papers, query=topic)
        progress_tracker.on_step_complete("Ranking papers", f"ranked {len(rankings)} papers")

        # Step 3: Build FAISS index
        self.vector_store.build_index(papers)

        # Step 4: Build Neo4j graph
        progress_tracker.on_step_start("Building citation graph")
        try:
            self.graph_service.connect()
            self.graph_service.clear_graph()
            self.graph_service.store_papers(papers)
            self.graph_service.store_citations(papers)
            self._inject_graph_service()
            progress_tracker.on_step_complete("Building citation graph", "graph built")
        except Exception as e:
            logger.error(f"Neo4j not available, continuing without graph: {e}")
            progress_tracker.on_step_error("Building citation graph", str(e))

        # Step 5: Run CrewAI pipeline
        inputs = {
            "topic": topic,
            "years": years,
            "min_papers": min_papers,
            "num_ideas": num_ideas,
        }

        agents = self._build_agents()
        tasks = self._build_tasks(agents, inputs)

        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
        )

        logger.info("Kicking off CrewAI pipeline...")
        crew_output = crew.kickoff(inputs=inputs)

        # Step 6: Gather results
        # Best base paper and top authors from Neo4j
        best_base_papers = []
        top_authors = []
        try:
            progress_tracker.on_step_start("Finding best base paper")
            best_base_papers = self.graph_service.find_best_base_paper(limit=5)
            progress_tracker.on_step_complete("Finding best base paper",
                                              best_base_papers[0].title if best_base_papers else "none found")

            progress_tracker.on_step_start("Finding top authors")
            top_authors = self.graph_service.find_top_authors(limit=10)
            progress_tracker.on_step_complete("Finding top authors", f"found {len(top_authors)} authors")
        except Exception as e:
            logger.error(f"Graph analysis error: {e}")

        # Clean up
        try:
            self.graph_service.close()
        except Exception:
            pass

        return {
            "topic": topic,
            "papers": [p.model_dump() for p in papers],
            "rankings": [r.model_dump() for r in rankings],
            "best_base_papers": [b.model_dump() for b in best_base_papers],
            "top_authors": [a.model_dump() for a in top_authors],
            "crew_output": crew_output.raw if hasattr(crew_output, "raw") else str(crew_output),
            "task_outputs": [
                {"task": t.description[:100], "output": t.output.raw if t.output else ""}
                for t in tasks
            ],
            "paper_count": len(papers),
        }
