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


class ScoreWeights(BaseModel):
    quant: float
    fundamental: float
    sentiment: float
    risk: float


class ModelProvenance(BaseModel):
    model_version: str
    feature_schema_version: str
    prediction_generated_at: str
    forecast_horizon_days: int
    upstream_latency_ms: float


class ConfidenceDiagnostics(BaseModel):
    raw_confidence: float
    calibrated_confidence: float
    disagreement_index: float
    stability_score: float
    confidence_decay_factor: float


class ExplainabilityMetadata(BaseModel):
    feature_importance: dict[str, float]
    top_positive_drivers: list[str]
    top_negative_drivers: list[str]


class BenchmarkMetrics(BaseModel):
    benchmark_symbol: str
    active_return: float
    tracking_error: float
    information_ratio: float
    relative_drawdown: float


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
    composite_score: float
    score_weights: ScoreWeights
    composite_formula_version: str
    confidence_diagnostics: ConfidenceDiagnostics
    explainability: ExplainabilityMetadata
    benchmark: BenchmarkMetrics
    market_regime: Literal["bull", "bear", "neutral"]
    volatility_regime: Literal["low", "medium", "high"]
    provenance: ModelProvenance
    drivers: list[str]
    warnings: list[str]
    summary: str
    schema_version: str


class PortfolioAsset(BaseModel):
    symbol: str
    exchange: Exchange = Exchange.NASDAQ
    weight: float | None = Field(default=None, ge=0)


class StressScenario(BaseModel):
    name: str
    shocked_return: float
    shocked_volatility: float
    shocked_var_95: float
    impact_pct: float


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
    stress_tests: list[StressScenario]
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
    benchmark_symbol: str
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
