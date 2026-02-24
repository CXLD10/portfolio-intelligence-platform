from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "portfolio-intelligence-platform")
    schema_version: str = os.getenv("SCHEMA_VERSION", "1.0")
    feature_schema_version: str = os.getenv("FEATURE_SCHEMA_VERSION", "1.0")
    composite_formula_version: str = os.getenv("COMPOSITE_FORMULA_VERSION", "2.0")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

    p1_base_url: str = os.getenv("P1_BASE_URL", "http://localhost:9001")
    p2_base_url: str = os.getenv("P2_BASE_URL", "http://localhost:9002")
    p1_api_key: str | None = os.getenv("P1_API_KEY")
    p2_api_key: str | None = os.getenv("P2_API_KEY")
    timeout_seconds: float = float(os.getenv("TIMEOUT_SECONDS", "8"))
    retry_attempts: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    retry_backoff_factor: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "0.3"))

    benchmark_symbol_nse: str = os.getenv("BENCHMARK_SYMBOL_NSE", "NIFTY50")
    benchmark_symbol_bse: str = os.getenv("BENCHMARK_SYMBOL_BSE", "SENSEX")
    benchmark_symbol_nasdaq: str = os.getenv("BENCHMARK_SYMBOL_NASDAQ", "SP500")
    risk_free_rate: float = float(os.getenv("RISK_FREE_RATE", "0.02"))
    intelligence_cache_ttl_s: int = int(os.getenv("INTELLIGENCE_CACHE_TTL_S", "30"))
    portfolio_cache_ttl_s: int = int(os.getenv("PORTFOLIO_CACHE_TTL_S", "45"))
    max_request_bytes: int = int(os.getenv("MAX_REQUEST_BYTES", "262144"))
    max_portfolio_assets: int = int(os.getenv("MAX_PORTFOLIO_ASSETS", "50"))
    max_backtest_period_days: int = int(os.getenv("MAX_BACKTEST_PERIOD_DAYS", "2000"))
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_s: int = int(os.getenv("RATE_LIMIT_WINDOW_S", "60"))


settings = Settings()
