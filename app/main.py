from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.v1 import router as v1_router
from app.config.settings import settings
from app.models.schemas import HealthResponse


def create_app() -> FastAPI:
    app = FastAPI(title="Portfolio Intelligence Platform", version=settings.schema_version)
    app.include_router(v1_router, prefix=settings.api_prefix)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=settings.app_name,
            timestamp=datetime.now(UTC),
            schema_version=settings.schema_version,
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "schema_version": settings.schema_version,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": str(exc),
                "schema_version": settings.schema_version,
            },
        )

    return app


app = create_app()
