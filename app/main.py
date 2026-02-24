from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.v1 import router as v1_router
from app.config.settings import settings
from app.integrations.http_common import UpstreamError
from app.integrations.project1_client import Project1Client
from app.integrations.project2_client import Project2Client
from app.models.schemas import Exchange, HealthResponse
from app.utils.observability import metrics_store


_HEALTH_CACHE = {"project1_status": "unknown", "project2_status": "unknown", "latency_ms": 0.0, "at": 0.0}


def _refresh_upstream_health() -> None:
    t0 = time.perf_counter()
    p1 = Project1Client()
    p2 = Project2Client()
    try:
        p1.get_market_status(Exchange.NSE)
        p1_status = "healthy"
    except Exception:
        p1_status = "unreachable"
    try:
        p2.get_prediction("AAPL", Exchange.NASDAQ)
        p2_status = "healthy"
    except Exception:
        p2_status = "unreachable"
    _HEALTH_CACHE.update(
        {
            "project1_status": p1_status,
            "project2_status": p2_status,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 3),
            "at": time.time(),
        }
    )
    metrics_store.record_upstream("project1", p1_status)
    metrics_store.record_upstream("project2", p2_status)


def create_app() -> FastAPI:
    app = FastAPI(title="Portfolio Intelligence Platform", version=settings.schema_version)
    app.include_router(v1_router, prefix=settings.api_prefix)

    rate_buckets: dict[str, deque[float]] = defaultdict(deque)

    @app.on_event("startup")
    async def startup_health_check() -> None:
        _refresh_upstream_health()

    @app.middleware("http")
    async def request_hardening_and_metrics(request: Request, call_next):
        body = await request.body()
        if len(body) > settings.max_request_bytes:
            return JSONResponse(
                status_code=413,
                content={"status": "error", "error_code": "REQUEST_TOO_LARGE", "message": "Request size exceeded", "schema_version": settings.schema_version},
            )

        client = request.client.host if request.client else "unknown"
        key = f"{client}:{request.url.path}"
        now = time.time()
        bucket = rate_buckets[key]
        while bucket and now - bucket[0] > settings.rate_limit_window_s:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_requests:
            return JSONResponse(
                status_code=429,
                content={"status": "error", "error_code": "RATE_LIMITED", "message": "Too many requests", "schema_version": settings.schema_version},
            )
        bucket.append(now)

        t0 = time.perf_counter()
        response = await call_next(request)
        latency_ms = (time.perf_counter() - t0) * 1000
        metrics_store.record_request(request.url.path, latency_ms, response.status_code >= 400)
        return response

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        if time.time() - _HEALTH_CACHE.get("at", 0) > 30:
            _refresh_upstream_health()
        status = "ok" if _HEALTH_CACHE["project1_status"] != "unreachable" or _HEALTH_CACHE["project2_status"] != "unreachable" else "degraded"
        return HealthResponse(
            status=status,
            service=settings.app_name,
            timestamp=datetime.now(UTC),
            project1_status=_HEALTH_CACHE["project1_status"],
            project2_status=_HEALTH_CACHE["project2_status"],
            latency_ms=float(_HEALTH_CACHE["latency_ms"]),
            schema_version=settings.schema_version,
        )

    @app.get("/metrics")
    def metrics() -> dict:
        snapshot = metrics_store.snapshot()
        snapshot["schema_version"] = settings.schema_version
        return snapshot

    @app.exception_handler(UpstreamError)
    async def upstream_error_handler(_: Request, exc: UpstreamError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"status": "error", "error_code": exc.code, "message": exc.message, "schema_version": settings.schema_version})

    @app.exception_handler(HTTPException)
    async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"status": "error", "error_code": f"HTTP_{exc.status_code}", "message": str(exc.detail), "schema_version": settings.schema_version})

    @app.exception_handler(Exception)
    async def generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"status": "error", "error_code": "INTERNAL_ERROR", "message": str(exc), "schema_version": settings.schema_version})

    return app


app = create_app()
