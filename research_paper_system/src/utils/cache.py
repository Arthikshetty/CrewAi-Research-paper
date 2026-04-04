"""Lightweight disk cache for API results — avoids redundant calls on re-runs."""

import hashlib
import json
import logging
import os
import time
from typing import Optional

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "cache")
DEFAULT_TTL = 24 * 60 * 60  # 24 hours


def _cache_path(key: str) -> str:
    safe = hashlib.sha256(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{safe}.json")


def get(key: str, ttl: int = DEFAULT_TTL) -> Optional[list]:
    """Return cached payload if it exists and hasn't expired, else None."""
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if time.time() - data.get("ts", 0) > ttl:
            os.remove(path)
            return None
        logger.debug("Cache HIT for %s", key)
        return data["payload"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def put(key: str, payload: list) -> None:
    """Write payload to disk cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = _cache_path(key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "payload": payload}, f, ensure_ascii=False, default=str)
        logger.debug("Cache STORE for %s", key)
    except OSError as exc:
        logger.warning("Could not write cache: %s", exc)


def clear() -> int:
    """Remove all cache files. Returns count of files removed."""
    if not os.path.isdir(CACHE_DIR):
        return 0
    count = 0
    for fname in os.listdir(CACHE_DIR):
        try:
            os.remove(os.path.join(CACHE_DIR, fname))
            count += 1
        except OSError:
            pass
    return count
