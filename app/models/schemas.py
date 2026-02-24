from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    NASDAQ = "NASDAQ"


class Recommendation(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error_code: str
    message: str
    schema_version: str


class IntelligenceResponse(BaseModel):
    exchange: Exchange
    symbol: str
    price: float
    recommendation: Recommendation
    confidence: float
    expected_return: float
    forecast_horizon: str
    risk_level: Literal["Low", "Moderate", "High"]
    quant_score: float
    fundamental_score: float
    sentiment_score: float
    risk_score: float
    drivers: list[str]
    warnings: list[str]
    summary: str
    schema_version: str


class PortfolioAsset(BaseModel):
    symbol: str
    exchange: Exchange = Exchange.NASDAQ
    weight: float | None = Field(default=None, ge=0)


class PortfolioEvaluateRequest(BaseModel):
    assets: list[PortfolioAsset] = Field(min_length=1)
    weighting_mode: Literal["manual", "confidence", "vol_target", "risk_parity", "kelly"] = "manual"


class PortfolioEvaluateResponse(BaseModel):
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    var_95: float
    max_drawdown_proxy: float
    beta_vs_benchmark: float
    concentration_index_hhi: float
    sector_exposure: dict[str, float]
    correlation_matrix: dict[str, dict[str, float]]
    risk_contribution: dict[str, float]
    schema_version: str


class BacktestResponse(BaseModel):
    symbol: str
    exchange: Exchange
    period_days: int
    strategy_return: float
    buy_hold_return: float
    max_drawdown: float
    win_rate: float
    avg_return_per_trade: float
    equity_curve: list[float]
    drawdown_curve: list[float]
    trade_log: list[dict[str, Any]]
    schema_version: str


class SentimentResponse(BaseModel):
    symbol: str
    exchange: Exchange
    sentiment_score: float
    bullish_ratio: float
    bearish_ratio: float
    momentum: float
    divergence_vs_price: float
    sentiment_trend: list[float]
    schema_version: str


class MarketOverviewResponse(BaseModel):
    sector_performance: dict[str, float]
    market_cap_distribution: dict[str, int]
    top_gainers: list[dict[str, float | str]]
    top_losers: list[dict[str, float | str]]
    volatility_snapshot: dict[str, float]
    exchange_health: dict[str, dict[str, float | str]]
    schema_version: str


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    schema_version: str
