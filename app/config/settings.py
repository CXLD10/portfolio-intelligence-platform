from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "portfolio-intelligence-platform"
    schema_version: str = "1.0"
    api_prefix: str = "/api/v1"
    benchmark_symbol: str = "SPY"
    risk_free_rate: float = 0.02


settings = Settings()
