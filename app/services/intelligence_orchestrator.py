from __future__ import annotations

import time

from app.config.settings import settings
from app.integrations.http_common import UpstreamError
from app.integrations.project1_client import Project1Client
from app.integrations.project2_client import Project2Client
from app.models.schemas import (
    BenchmarkMetrics,
    ConfidenceDiagnostics,
    Exchange,
    ExplainabilityMetadata,
    IntelligenceResponse,
    ModelProvenance,
    Recommendation,
    ScoreWeights,
)
from app.services.agent_reasoning_engine import AgentReasoningEngine
from app.services.benchmark_engine import BenchmarkEngine, benchmark_symbol_for_exchange
from app.services.sentiment_engine import SentimentEngine
from app.utils.cache import TTLCache
from app.utils.math_utils import returns_from_prices
from app.utils.normalization import clamp, normalize_symbol
from app.utils.observability import metrics_store
from app.utils.validation import filter_valid_numeric_map


class IntelligenceOrchestrator:
    def __init__(self) -> None:
        self.p1 = Project1Client()
        self.p2 = Project2Client()
        self.sentiment = SentimentEngine()
        self.reasoning = AgentReasoningEngine()
        self.benchmark = BenchmarkEngine()
        self.cache = TTLCache()

    def _fundamental_score(self, fundamentals: dict[str, float | str]) -> float:
        numeric = filter_valid_numeric_map({"roe": fundamentals.get("roe"), "revenue_growth": fundamentals.get("revenue_growth"), "debt_to_equity": fundamentals.get("debt_to_equity")})
        roe = numeric.get("roe", 0.05)
        rev = numeric.get("revenue_growth", 0)
        debt = numeric.get("debt_to_equity", 1)
        score = 0.5 * clamp(roe / 0.25, 0, 1) + 0.35 * clamp((rev + 0.1) / 0.4, 0, 1) + 0.15 * (1 - clamp(debt / 2, 0, 1))
        return round(clamp(score, 0, 1), 4)

    def _quant_score(self, prediction: dict[str, float], features: dict[str, float]) -> float:
        conf = float(prediction.get("confidence", 0.5))
        expected = float(prediction.get("expected_return", 0))
        vol = float(features.get("volatility", 0.3))
        dd = abs(float(features.get("drawdown", -0.2)))
        score = 0.45 * conf + 0.3 * clamp((expected + 0.1) / 0.2, 0, 1) + 0.25 * (1 - clamp((vol + dd) / 1.2, 0, 1))
        return round(clamp(score, 0, 1), 4)

    def _risk_score(self, prediction: dict[str, float], features: dict[str, float]) -> float:
        model_risk = float(prediction.get("risk_score", 0.5))
        vol = float(features.get("volatility", 0.2))
        dd = abs(float(features.get("drawdown", -0.2)))
        score = 0.5 * model_risk + 0.3 * clamp(vol / 0.8, 0, 1) + 0.2 * clamp(dd / 0.5, 0, 1)
        return round(clamp(score, 0, 1), 4)

    def _confidence_calibration(self, raw_confidence: float, quant: float, sentiment: float, vol: float) -> ConfidenceDiagnostics:
        disagreement = abs(quant - sentiment)
        volatility_adjustment = 1 - clamp(vol / 1.0, 0, 0.5)
        decay = 0.97
        calibrated = clamp(raw_confidence * volatility_adjustment * (1 - 0.35 * disagreement) * decay, 0, 1)
        stability = clamp(1 - (0.5 * disagreement + 0.5 * (1 - volatility_adjustment)), 0, 1)
        return ConfidenceDiagnostics(
            raw_confidence=round(raw_confidence, 4),
            calibrated_confidence=round(calibrated, 4),
            disagreement_index=round(disagreement, 4),
            stability_score=round(stability, 4),
            confidence_decay_factor=decay,
        )

    def run(self, symbol: str, exchange: Exchange) -> IntelligenceResponse:
        symbol = normalize_symbol(symbol)
        key = f"{exchange.value}:{symbol}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        t0 = time.perf_counter()
        p1_error = None
        p2_error = None
        try:
            quote = self.p1.get_quote(symbol, exchange)
            fundamentals = self.p1.get_fundamentals(symbol, exchange)
            hist = self.p1.get_historical(symbol, exchange, 252)
            metrics_store.record_upstream("project1", "healthy")
        except UpstreamError as exc:
            p1_error = exc
            metrics_store.record_upstream("project1", "unreachable")
            quote = {"price": 0.0, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
            fundamentals = {"roe": 0.05, "revenue_growth": 0.0, "debt_to_equity": 1.0}
            hist = []

        try:
            prediction = self.p2.get_prediction(symbol, exchange)
            features = self.p2.get_features(symbol, exchange)
            try:
                risk_payload = self.p2.get_risk(symbol, exchange)
                prediction["risk_score"] = risk_payload["risk_score"]
            except UpstreamError:
                pass
            metrics_store.record_upstream("project2", "healthy")
        except UpstreamError as exc:
            p2_error = exc
            metrics_store.record_upstream("project2", "unreachable")
            prediction = {"prediction": "HOLD", "confidence": 0.5, "expected_return": 0.0, "risk_score": 0.5, "forecast_horizon": "5d", "model_version": "unknown"}
            features = {"volatility": 0.2, "drawdown": -0.2}

        if p1_error and p2_error:
            raise UpstreamError("project1", "UPSTREAM_BOTH_UNAVAILABLE", f"project1={p1_error.message}; project2={p2_error.message}")

        sent = self.sentiment.compute(symbol, exchange)
        quant = self._quant_score(prediction, features)
        fundamental = self._fundamental_score(fundamentals)
        risk = self._risk_score(prediction, features)
        sentiment = clamp((sent.sentiment_score + 1) / 2, 0, 1)

        weights = ScoreWeights(quant=0.5, fundamental=0.3, sentiment=0.2, risk=0.35)
        composite = clamp(weights.quant * quant + weights.fundamental * fundamental + weights.sentiment * sentiment - weights.risk * risk, 0, 1)
        confidence_diag = self._confidence_calibration(float(prediction.get("confidence", 0.5)), quant, sentiment, float(features.get("volatility", 0.2)))
        reasoned = self.reasoning.compute(quant, fundamental, sentiment, risk)

        bench_symbol = benchmark_symbol_for_exchange(exchange)
        try:
            bench_hist = self.p1.get_historical(bench_symbol, exchange, 252)
            bm = BenchmarkMetrics(**self.benchmark.compare(returns_from_prices([x["close"] for x in hist]), returns_from_prices([x["close"] for x in bench_hist]), bench_symbol))
        except Exception:
            bm = BenchmarkMetrics(benchmark_symbol=bench_symbol, active_return=0.0, tracking_error=0.0, information_ratio=0.0, relative_drawdown=0.0)

        vol = float(features.get("volatility", 0.2))
        regime = "bull" if float(prediction.get("expected_return", 0)) > 0.02 else "bear" if float(prediction.get("expected_return", 0)) < -0.02 else "neutral"
        vol_regime = "low" if vol < 0.18 else "medium" if vol < 0.32 else "high"

        explainability = ExplainabilityMetadata(
            feature_importance={"probability_up": 0.34, "volatility": 0.23, "drawdown": 0.18, "roe": 0.15, "sentiment_score": 0.10},
            top_positive_drivers=["probability_up", "roe", "sentiment_score"],
            top_negative_drivers=["volatility", "drawdown"],
        )

        latency_ms = (time.perf_counter() - t0) * 1000
        provenance = ModelProvenance(
            model_version=str(prediction.get("model_version", "unknown")),
            feature_schema_version=settings.feature_schema_version,
            prediction_generated_at=str(quote.get("timestamp")),
            forecast_horizon_days=int(str(prediction.get("forecast_horizon", "5d")).replace("d", "")),
            upstream_latency_ms=round(latency_ms, 3),
        )

        degraded = p1_error is not None or p2_error is not None
        degraded_source = "project1" if p1_error is not None else "project2" if p2_error is not None else None

        out = IntelligenceResponse(
            degraded=degraded,
            degraded_source=degraded_source,
            exchange=exchange,
            symbol=symbol,
            price=float(quote.get("price", 0.0)),
            recommendation=Recommendation(reasoned["recommendation"]),
            confidence=confidence_diag.calibrated_confidence,
            expected_return=float(prediction.get("expected_return", 0.0)),
            forecast_horizon=str(prediction.get("forecast_horizon", "5d")),
            risk_level=reasoned["risk_level"],
            quant_score=quant,
            fundamental_score=fundamental,
            sentiment_score=round(sentiment, 4),
            risk_score=risk,
            composite_score=round(composite, 4),
            score_weights=weights,
            composite_formula_version=settings.composite_formula_version,
            confidence_diagnostics=confidence_diag,
            explainability=explainability,
            benchmark=bm,
            market_regime=regime,
            volatility_regime=vol_regime,
            provenance=provenance,
            drivers=reasoned["drivers"],
            warnings=reasoned["warnings"] + ([f"degraded_source={degraded_source}"] if degraded_source else []),
            summary=reasoned["summary"],
            schema_version=settings.schema_version,
        )
        self.cache.set(key, out, settings.intelligence_cache_ttl_s)
        return out
