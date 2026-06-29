import time

from django.core.cache import cache


def is_rate_limited(key: str, *, limit: int = 10, window: int = 60) -> bool:
    cache_key = f"lead-rate:{key}"
    now = int(time.time())
    bucket = cache.get(cache_key, {"count": 0, "start": now})
    if now - bucket["start"] >= window:
        bucket = {"count": 0, "start": now}
    bucket["count"] += 1
    cache.set(cache_key, bucket, window)
    return bucket["count"] > limit
