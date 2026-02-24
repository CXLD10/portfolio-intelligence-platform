from __future__ import annotations

import time
from typing import Any


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        value = self._store.get(key)
        if value is None:
            return None
        exp, payload = value
        if exp < time.time():
            self._store.pop(key, None)
            return None
        return payload

    def set(self, key: str, payload: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, payload)
