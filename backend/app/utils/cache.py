"""
In-process TTL cache for the public post feed.
Deliberately simple (no Redis dependency) so the project runs with zero
external services out of the box; swapping this for Redis in production is
called out explicitly in ARCHITECTURE.md.
"""
import time
from typing import Any, Callable

_store: dict[str, tuple[float, Any]] = {}


def cached(ttl_seconds: int):
    def decorator(fn: Callable):
        def wrapper(*args, cache_key: str, **kwargs):
            now = time.time()
            hit = _store.get(cache_key)
            if hit and hit[0] > now:
                return hit[1]
            result = fn(*args, **kwargs)
            _store[cache_key] = (now + ttl_seconds, result)
            return result
        return wrapper
    return decorator


def invalidate_prefix(prefix: str) -> None:
    """Called whenever a post is created/updated/deleted so stale list pages
    aren't served from cache."""
    for key in list(_store.keys()):
        if key.startswith(prefix):
            _store.pop(key, None)
