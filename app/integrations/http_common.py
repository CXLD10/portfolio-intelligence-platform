from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from app.config.settings import settings
from app.utils.observability import metrics_store


@dataclass
class UpstreamError(Exception):
    source: str
    code: str
    message: str
    status_code: int = 503


class BaseHttpIntegration:
    source: str = "upstream"

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = settings.timeout_seconds
        self.retries = settings.retry_attempts
        self.backoff = settings.retry_backoff_factor

    def _headers(self) -> dict[str, str]:
        h = {"accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _get(self, path: str, params: dict[str, str | int]) -> dict:
        url = f"{self.base_url}{path}"
        last_exc: Exception | None = None
        for attempt in range(1, self.retries + 1):
            t0 = time.perf_counter()
            try:
                with httpx.Client(timeout=self.timeout, headers=self._headers()) as client:
                    resp = client.get(url, params=params)
                latency = (time.perf_counter() - t0) * 1000
                metrics_store.record_upstream_latency(self.source, latency)

                if 500 <= resp.status_code < 600:
                    metrics_store.record_upstream_failure(self.source)
                    if attempt < self.retries:
                        metrics_store.record_upstream_retry(self.source)
                        time.sleep(self.backoff * (2 ** (attempt - 1)))
                        continue
                    raise UpstreamError(self.source, f"UPSTREAM_{self.source.upper()}_UNAVAILABLE", f"{self.source} returned {resp.status_code}")

                if 400 <= resp.status_code < 500:
                    detail = resp.text
                    try:
                        body = resp.json()
                        detail = body.get("message") or body.get("error") or detail
                    except Exception:
                        pass
                    raise UpstreamError(self.source, f"UPSTREAM_{self.source.upper()}_CLIENT_ERROR", detail, status_code=resp.status_code)

                try:
                    return resp.json()
                except Exception as exc:
                    raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", f"Invalid JSON from {self.source}") from exc

            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as exc:
                last_exc = exc
                metrics_store.record_upstream_timeout(self.source)
                if attempt < self.retries:
                    metrics_store.record_upstream_retry(self.source)
                    time.sleep(self.backoff * (2 ** (attempt - 1)))
                    continue
                raise UpstreamError(self.source, f"UPSTREAM_{self.source.upper()}_UNAVAILABLE", str(exc)) from exc

        raise UpstreamError(self.source, f"UPSTREAM_{self.source.upper()}_UNAVAILABLE", str(last_exc) if last_exc else "unknown")
