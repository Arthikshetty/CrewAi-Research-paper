import logging
from typing import Dict, List, Optional, Tuple
from thefuzz import fuzz
from src.models.paper import Paper

logger = logging.getLogger(__name__)

DOI_MATCH_THRESHOLD = 100  # Exact
TITLE_MATCH_THRESHOLD = 90  # Fuzzy


class Deduplicator:
    """Cross-source paper deduplication by DOI (exact) and title (fuzzy)."""

    def deduplicate(self, papers: List[Paper]) -> List[Paper]:
        doi_map: Dict[str, Paper] = {}
        no_doi: List[Paper] = []

        # Group by DOI first
        for paper in papers:
            if paper.doi:
                key = paper.doi.lower().strip()
                if key in doi_map:
                    doi_map[key] = self._merge(doi_map[key], paper)
                else:
                    doi_map[key] = paper
            else:
                no_doi.append(paper)

        # Fuzzy-match remaining papers by title
        unique = list(doi_map.values())
        for paper in no_doi:
            matched = False
            for i, existing in enumerate(unique):
                score = fuzz.ratio(
                    paper.title.lower().strip(),
                    existing.title.lower().strip(),
                )
                if score >= TITLE_MATCH_THRESHOLD:
                    unique[i] = self._merge(existing, paper)
                    matched = True
                    break
            if not matched:
                unique.append(paper)

        logger.info(f"Deduplication: {len(papers)} → {len(unique)} papers")
        return unique

    def _merge(self, primary: Paper, secondary: Paper) -> Paper:
        """Merge metadata from secondary into primary, preferring non-empty values."""
        if not primary.abstract and secondary.abstract:
            primary.abstract = secondary.abstract
        if not primary.doi and secondary.doi:
            primary.doi = secondary.doi
        if not primary.pdf_url and secondary.pdf_url:
            primary.pdf_url = secondary.pdf_url
        if secondary.citations_count > primary.citations_count:
            primary.citations_count = secondary.citations_count
        if not primary.journal_name and secondary.journal_name:
            primary.journal_name = secondary.journal_name
        if not primary.conference_name and secondary.conference_name:
            primary.conference_name = secondary.conference_name
        if not primary.keywords and secondary.keywords:
            primary.keywords = secondary.keywords
        if not primary.year and secondary.year:
            primary.year = secondary.year
        if not primary.authors and secondary.authors:
            primary.authors = secondary.authors
        # Merge references lists
        existing_refs = set(primary.references)
        for ref in secondary.references:
            if ref not in existing_refs:
                primary.references.append(ref)
        return primary


deduplicator = Deduplicator()
