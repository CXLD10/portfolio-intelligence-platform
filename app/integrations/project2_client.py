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

    def get_prediction(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get("/prediction", {"symbol": symbol, "exchange": exchange.value})
        try:
            return P2Prediction(**raw).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc

    def get_features(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get("/features", {"symbol": symbol, "exchange": exchange.value})
        if isinstance(raw, dict) and "features" in raw and isinstance(raw["features"], list) and raw["features"]:
            f = raw["features"][-1]
        else:
            f = raw
        try:
            return P2Features(**f).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc

    def get_risk(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get("/risk", {"symbol": symbol, "exchange": exchange.value})
        try:
            return P2Risk(**raw).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc
