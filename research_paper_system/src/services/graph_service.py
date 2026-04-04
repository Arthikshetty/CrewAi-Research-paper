import logging
from typing import Dict, List, Optional
from src.models.paper import Paper, Author
from src.models.analysis import BasePaperResult, TopAuthorResult

logger = logging.getLogger(__name__)


class GraphService:
    """Neo4j knowledge graph service for citation analysis."""

    def __init__(self, uri: str, user: str, password: str):
        self._driver = None
        self._uri = uri
        self._user = user
        self._password = password

    def connect(self):
        from neo4j import GraphDatabase
        self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
        self._driver.verify_connectivity()
        logger.info("Connected to Neo4j")

    def close(self):
        if self._driver:
            self._driver.close()

    def clear_graph(self):
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Neo4j graph cleared")

    def store_papers(self, papers: List[Paper]):
        with self._driver.session() as session:
            for paper in papers:
                # Create Paper node
                session.run(
                    """
                    MERGE (p:Paper {paper_id: $id})
                    SET p.title = $title,
                        p.year = $year,
                        p.abstract = $abstract,
                        p.source = $source,
                        p.citation_count = $citation_count,
                        p.doi = $doi,
                        p.url = $url
                    """,
                    id=paper.id,
                    title=paper.title,
                    year=paper.year,
                    abstract=(paper.abstract or "")[:500],
                    source=paper.source.value,
                    citation_count=paper.citations_count,
                    doi=paper.doi,
                    url=paper.url,
                )
                # Create Author nodes and AUTHORED relationships
                for author in paper.authors:
                    session.run(
                        """
                        MERGE (a:Author {name: $name})
                        SET a.orcid = $orcid
                        WITH a
                        MATCH (p:Paper {paper_id: $paper_id})
                        MERGE (a)-[:AUTHORED]->(p)
                        """,
                        name=author.name,
                        orcid=author.orcid,
                        paper_id=paper.id,
                    )

                # Create co-authorship edges
                if len(paper.authors) > 1:
                    for i, a1 in enumerate(paper.authors):
                        for a2 in paper.authors[i + 1:]:
                            session.run(
                                """
                                MATCH (a1:Author {name: $name1}), (a2:Author {name: $name2})
                                MERGE (a1)-[:COLLABORATES_WITH]-(a2)
                                """,
                                name1=a1.name,
                                name2=a2.name,
                            )

        logger.info(f"Stored {len(papers)} papers in Neo4j")

    def store_citations(self, papers: List[Paper]):
        """Build CITES relationships based on DOI references."""
        doi_to_id = {}
        for p in papers:
            if p.doi:
                doi_to_id[p.doi.lower()] = p.id

        with self._driver.session() as session:
            for paper in papers:
                for ref_doi in paper.references:
                    ref_id = doi_to_id.get(ref_doi.lower())
                    if ref_id:
                        session.run(
                            """
                            MATCH (p1:Paper {paper_id: $from_id}), (p2:Paper {paper_id: $to_id})
                            MERGE (p1)-[:CITES]->(p2)
                            """,
                            from_id=paper.id,
                            to_id=ref_id,
                        )
        logger.info("Citation relationships stored")

    def find_best_base_paper(self, limit: int = 5) -> List[BasePaperResult]:
        results = []
        with self._driver.session() as session:
            # In-degree analysis: papers most cited BY other discovered papers
            records = session.run(
                """
                MATCH (p:Paper)<-[r:CITES]-(citing:Paper)
                WITH p, count(r) AS in_degree, collect(citing.title) AS cited_by_titles
                ORDER BY in_degree DESC, p.citation_count DESC
                LIMIT $limit
                RETURN p.paper_id AS id, p.title AS title, p.year AS year,
                       p.source AS source, p.citation_count AS global_citations,
                       in_degree, cited_by_titles
                """,
                limit=limit,
            )
            for record in records:
                results.append(BasePaperResult(
                    paper_id=record["id"],
                    title=record["title"],
                    total_incoming_citations=record["in_degree"],
                    total_global_citations=record["global_citations"] or 0,
                    pagerank_score=record["in_degree"],  # Simplified; real PageRank below
                    referenced_by=record["cited_by_titles"][:10],
                    year=record["year"],
                    source=record["source"] or "",
                ))

        # Try PageRank if GDS is available
        try:
            self._run_pagerank(results)
        except Exception as e:
            logger.warning(f"PageRank not available (Neo4j GDS plugin needed): {e}")
            # Fallback: use in-degree as proxy for PageRank
            if results:
                max_in = max(r.total_incoming_citations for r in results) or 1
                for r in results:
                    r.pagerank_score = r.total_incoming_citations / max_in

        return results

    def _run_pagerank(self, results: List[BasePaperResult]):
        with self._driver.session() as session:
            # Check if GDS is available by trying the pageRank call
            records = session.run(
                """
                CALL gds.pageRank.stream({
                    nodeProjection: 'Paper',
                    relationshipProjection: 'CITES'
                })
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) AS paper, score
                ORDER BY score DESC
                LIMIT 10
                RETURN paper.paper_id AS id, score
                """
            )
            pr_scores = {r["id"]: r["score"] for r in records}
            for result in results:
                if result.paper_id in pr_scores:
                    result.pagerank_score = pr_scores[result.paper_id]

    def find_top_authors(self, limit: int = 10) -> List[TopAuthorResult]:
        results = []
        with self._driver.session() as session:
            records = session.run(
                """
                MATCH (a:Author)-[:AUTHORED]->(p:Paper)
                WITH a, count(p) AS paper_count,
                     sum(p.citation_count) AS total_cites,
                     collect(p) AS papers,
                     min(p.year) AS first_year,
                     max(p.year) AS last_year
                ORDER BY paper_count DESC, total_cites DESC
                LIMIT $limit
                RETURN a.name AS name, a.orcid AS orcid,
                       paper_count, total_cites,
                       first_year, last_year,
                       [p IN papers | p.title] AS paper_titles,
                       [p IN papers | p.citation_count] AS paper_citations
                """,
                limit=limit,
            )
            for record in records:
                paper_titles = record["paper_titles"] or []
                paper_citations = record["paper_citations"] or []

                # Find most cited paper
                most_cited = None
                if paper_titles and paper_citations:
                    max_idx = paper_citations.index(max(paper_citations))
                    most_cited = paper_titles[max_idx]

                first_year = record["first_year"]
                last_year = record["last_year"]
                year_range = ""
                if first_year and last_year:
                    year_range = f"{first_year}-{last_year}"

                results.append(TopAuthorResult(
                    author_name=record["name"],
                    orcid=record["orcid"],
                    total_papers_on_topic=record["paper_count"],
                    total_citations=record["total_cites"] or 0,
                    most_cited_paper=most_cited,
                    year_range_active=year_range,
                ))

        return results

    def get_citation_network(self, paper_title: str, depth: int = 2) -> Dict:
        with self._driver.session() as session:
            records = session.run(
                """
                MATCH (p:Paper)
                WHERE toLower(p.title) CONTAINS toLower($title)
                CALL {
                    WITH p
                    MATCH path = (p)-[:CITES*1..2]-(related:Paper)
                    RETURN related.title AS related_title,
                           related.citation_count AS citations,
                           length(path) AS distance
                }
                RETURN p.title AS center, collect({
                    title: related_title, citations: citations, distance: distance
                }) AS network
                LIMIT 1
                """,
                title=paper_title,
            )
            for record in records:
                return {
                    "center": record["center"],
                    "network": record["network"][:50],
                }
        return {"center": paper_title, "network": []}

    def get_author_network(self, author_name: str) -> Dict:
        with self._driver.session() as session:
            records = session.run(
                """
                MATCH (a:Author {name: $name})-[:COLLABORATES_WITH]-(coauthor:Author)
                MATCH (coauthor)-[:AUTHORED]->(p:Paper)
                WITH coauthor, count(p) AS shared_papers
                ORDER BY shared_papers DESC
                LIMIT 20
                RETURN coauthor.name AS name, shared_papers
                """,
                name=author_name,
            )
            collaborators = [{"name": r["name"], "shared_papers": r["shared_papers"]} for r in records]
            return {"author": author_name, "collaborators": collaborators}

    def get_publication_trends(self) -> List[Dict]:
        with self._driver.session() as session:
            records = session.run(
                """
                MATCH (p:Paper)
                WHERE p.year IS NOT NULL
                RETURN p.year AS year, count(p) AS count
                ORDER BY year
                """
            )
            return [{"year": r["year"], "count": r["count"]} for r in records]
