from __future__ import annotations

from collections import defaultdict


class MetricsStore:
    def __init__(self) -> None:
        self.request_count = 0
        self.error_count = 0
        self.endpoint_count: dict[str, int] = defaultdict(int)
        self.endpoint_latency_ms_sum: dict[str, float] = defaultdict(float)
        self.upstream_status: dict[str, str] = {"project1": "unknown", "project2": "unknown"}

    def record_request(self, path: str, latency_ms: float, is_error: bool) -> None:
        self.request_count += 1
        self.endpoint_count[path] += 1
        self.endpoint_latency_ms_sum[path] += latency_ms
        if is_error:
            self.error_count += 1

    def record_upstream(self, name: str, status: str) -> None:
        self.upstream_status[name] = status

    def snapshot(self) -> dict:
        avg = {
            p: (self.endpoint_latency_ms_sum[p] / self.endpoint_count[p]) if self.endpoint_count[p] else 0
            for p in self.endpoint_count
        }
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.request_count) if self.request_count else 0,
            "per_endpoint_count": dict(self.endpoint_count),
            "per_endpoint_avg_latency_ms": avg,
            "upstream_status": self.upstream_status,
        }


metrics_store = MetricsStore()
