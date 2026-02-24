from __future__ import annotations

from collections import defaultdict


class MetricsStore:
    def __init__(self) -> None:
        self.request_count = 0
        self.error_count = 0
        self.endpoint_count: dict[str, int] = defaultdict(int)
        self.endpoint_latency_ms_sum: dict[str, float] = defaultdict(float)
        self.upstream_status: dict[str, str] = {"project1": "unknown", "project2": "unknown"}
        self.upstream_latency_ms_sum: dict[str, float] = defaultdict(float)
        self.upstream_calls: dict[str, int] = defaultdict(int)
        self.upstream_failures: dict[str, int] = defaultdict(int)
        self.upstream_timeouts: dict[str, int] = defaultdict(int)
        self.upstream_retries: dict[str, int] = defaultdict(int)

    def record_request(self, path: str, latency_ms: float, is_error: bool) -> None:
        self.request_count += 1
        self.endpoint_count[path] += 1
        self.endpoint_latency_ms_sum[path] += latency_ms
        if is_error:
            self.error_count += 1

    def record_upstream(self, name: str, status: str) -> None:
        self.upstream_status[name] = status

    def record_upstream_latency(self, name: str, latency_ms: float) -> None:
        self.upstream_calls[name] += 1
        self.upstream_latency_ms_sum[name] += latency_ms

    def record_upstream_failure(self, name: str) -> None:
        self.upstream_failures[name] += 1

    def record_upstream_timeout(self, name: str) -> None:
        self.upstream_timeouts[name] += 1

    def record_upstream_retry(self, name: str) -> None:
        self.upstream_retries[name] += 1

    def snapshot(self) -> dict:
        avg = {p: (self.endpoint_latency_ms_sum[p] / self.endpoint_count[p]) if self.endpoint_count[p] else 0 for p in self.endpoint_count}
        upstream_avg = {u: (self.upstream_latency_ms_sum[u] / self.upstream_calls[u]) if self.upstream_calls[u] else 0 for u in set(list(self.upstream_calls.keys()) + ["project1", "project2"]) }
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.request_count) if self.request_count else 0,
            "per_endpoint_count": dict(self.endpoint_count),
            "per_endpoint_avg_latency_ms": avg,
            "upstream_status": self.upstream_status,
            "upstream_avg_latency_ms": upstream_avg,
            "upstream_failures": dict(self.upstream_failures),
            "upstream_timeouts": dict(self.upstream_timeouts),
            "upstream_retries": dict(self.upstream_retries),
        }


metrics_store = MetricsStore()
