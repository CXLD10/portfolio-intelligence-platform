from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "portfolio-intelligence-platform"
    schema_version: str = "1.0"
    feature_schema_version: str = "1.0"
    composite_formula_version: str = "2.0"
    api_prefix: str = "/api/v1"
    benchmark_symbol_nse: str = "NIFTY50"
    benchmark_symbol_bse: str = "SENSEX"
    benchmark_symbol_nasdaq: str = "SP500"
    risk_free_rate: float = 0.02
    intelligence_cache_ttl_s: int = 30
    portfolio_cache_ttl_s: int = 45
    max_request_bytes: int = 262_144
    max_portfolio_assets: int = 50
    max_backtest_period_days: int = 2000
    rate_limit_requests: int = 120
    rate_limit_window_s: int = 60


settings = Settings()
