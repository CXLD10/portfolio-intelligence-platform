from __future__ import annotations

from pydantic import BaseModel, ValidationError

from app.config.settings import settings
from app.integrations.http_common import BaseHttpIntegration, UpstreamError
from app.models.schemas import Exchange


class P2Prediction(BaseModel):
    prediction: str
    confidence: float
    probability_up: float
    probability_down: float
    expected_return: float
    risk_score: float
    forecast_horizon: str
    model_version: str


class P2Features(BaseModel):
    volatility: float
    sharpe_ratio: float
    beta: float
    drawdown: float


class P2Risk(BaseModel):
    risk_score: float


class Project2Client(BaseHttpIntegration):
    source = "project2"

    def __init__(self) -> None:
        super().__init__(base_url=settings.p2_base_url, api_key=settings.p2_api_key)

    def _get_with_fallback(self, paths: list[str], params: dict[str, str]) -> dict:
        last_exc: UpstreamError | None = None
        for path in paths:
            try:
                raw = self._get(path, params)
                if isinstance(raw, dict):
                    return raw
                raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", f"unexpected response type from {path}")
            except UpstreamError as exc:
                if exc.status_code == 404:
                    last_exc = exc
                    continue
                raise
        if last_exc:
            raise last_exc
        raise UpstreamError(self.source, "UPSTREAM_PROJECT2_UNAVAILABLE", "project2 endpoint unavailable")

    def get_prediction(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get_with_fallback(
            ["/api/v1/predict", "/predict", "/prediction"],
            {"symbol": symbol, "exchange": exchange.value},
        )
        if "prediction" not in raw and "signal" in raw:
            raw = {
                "prediction": str(raw.get("signal", "HOLD")),
                "confidence": float(raw.get("confidence", 0.5)),
                "probability_up": float(raw.get("probability_up", raw.get("prob_up", 0.5))),
                "probability_down": float(raw.get("probability_down", raw.get("prob_down", 0.5))),
                "expected_return": float(raw.get("expected_return", 0.0)),
                "risk_score": float(raw.get("risk_score", 0.5)),
                "forecast_horizon": str(raw.get("forecast_horizon", "5d")),
                "model_version": str(raw.get("model_version", "unknown")),
            }
        try:
            return P2Prediction(**raw).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc

    def get_features(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get_with_fallback(
            ["/api/v1/features", "/features"],
            {"symbol": symbol, "exchange": exchange.value},
        )
        if isinstance(raw, dict) and "features" in raw and isinstance(raw["features"], list) and raw["features"]:
            f = raw["features"][-1]
        else:
            f = raw
        try:
            return P2Features(**f).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc

    def get_risk(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get_with_fallback(
            ["/api/v1/risk", "/risk"],
            {"symbol": symbol, "exchange": exchange.value},
        )
        try:
            return P2Risk(**raw).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc
