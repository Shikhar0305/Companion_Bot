"""Simple in-process token-bucket rate limiter (docs/09 §S2).

Production swaps in a Redis-backed limiter shared across workers; same interface.
"""
from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.capacity = per_minute
        self.refill_per_sec = per_minute / 60.0
        self._tokens: dict[str, float] = defaultdict(lambda: per_minute)
        self._last: dict[str, float] = defaultdict(time.monotonic)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        elapsed = now - self._last[key]
        self._last[key] = now
        self._tokens[key] = min(self.capacity, self._tokens[key] + elapsed * self.refill_per_sec)
        if self._tokens[key] >= 1.0:
            self._tokens[key] -= 1.0
            return True
        return False
