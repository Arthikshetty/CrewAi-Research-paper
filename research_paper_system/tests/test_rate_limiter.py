import pytest
from src.utils.rate_limiter import RateLimiter


def test_rate_limiter_allows_first_call():
    limiter = RateLimiter()
    limiter.wait("test_source", delay=0.01)


def test_rate_limiter_per_source():
    limiter = RateLimiter()
    limiter.wait("source_a", delay=0.01)
    limiter.wait("source_b", delay=0.01)
