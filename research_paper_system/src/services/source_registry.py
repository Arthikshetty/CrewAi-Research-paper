import os
import logging
from typing import Dict, List
from src.config.settings import SOURCES, SourceConfig

logger = logging.getLogger(__name__)


class SourceRegistry:
    """Detects which academic sources are available based on configured API keys."""

    def __init__(self):
        self._sources: Dict[str, SourceConfig] = {}
        self._detect_available_sources()

    def _detect_available_sources(self):
        for key, config in SOURCES.items():
            if config.api_key_env:
                api_key = os.getenv(config.api_key_env, "")
                if api_key:
                    self._sources[key] = config
                    logger.info(f"✅ {config.name}: ACTIVE (API key found)")
                else:
                    # Sources that work without a key but benefit from one
                    if key in ("semantic_scholar", "core", "pubmed", "openalex"):
                        self._sources[key] = config
                        logger.info(f"⚠️ {config.name}: ACTIVE (no key, using public rate limits)")
                    elif key == "google_scholar":
                        # Try scholarly (no key needed)
                        self._sources[key] = config
                        logger.info(f"⚠️ {config.name}: ACTIVE (using scholarly lib, may be rate-limited)")
                    else:
                        logger.warning(f"❌ {config.name}: SKIPPED (no API key for {config.api_key_env})")
            else:
                # No key required (arxiv, crossref, dblp)
                self._sources[key] = config
                logger.info(f"✅ {config.name}: ACTIVE (no key required)")

    def get_active_sources(self) -> Dict[str, SourceConfig]:
        return self._sources

    def get_active_source_names(self) -> List[str]:
        return list(self._sources.keys())

    def is_active(self, source_key: str) -> bool:
        return source_key in self._sources

    def get_config(self, source_key: str) -> SourceConfig:
        return self._sources[source_key]


source_registry = SourceRegistry()
