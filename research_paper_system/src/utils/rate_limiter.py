import time
import threading
from collections import defaultdict


class RateLimiter:
    """Per-source token-bucket rate limiter. Thread-safe."""

    def __init__(self):
        self._last_call: dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    def wait(self, source_key: str, delay_seconds: float):
        with self._lock:
            now = time.time()
            elapsed = now - self._last_call[source_key]
            if elapsed < delay_seconds:
                wait_time = delay_seconds - elapsed
                time.sleep(wait_time)
            self._last_call[source_key] = time.time()


rate_limiter = RateLimiter()
