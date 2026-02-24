from __future__ import annotations

from pydantic import BaseModel, ValidationError

from app.config.settings import settings
from app.integrations.http_common import BaseHttpIntegration, UpstreamError
from app.models.schemas import Exchange


class P1Quote(BaseModel):
    symbol: str
    exchange: str
    price: float
    volume: float
    currency: str
    timestamp: str


class P1Fundamentals(BaseModel):
    market_cap: float
    sector: str
    industry: str
    debt_to_equity: float
    roe: float
    revenue_growth: float


class P1HistoricalItem(BaseModel):
    timestamp: str
    close: float


class P1MarketStatus(BaseModel):
    exchange: str
    session: str | None = None
    is_open: bool | None = None


class Project1Client(BaseHttpIntegration):
    source = "project1"

    def __init__(self) -> None:
        super().__init__(base_url=settings.p1_base_url, api_key=settings.p1_api_key)

    def get_quote(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get("/quote", {"symbol": symbol, "exchange": exchange.value})
        try:
            return P1Quote(**raw).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc

    def get_fundamentals(self, symbol: str, exchange: Exchange) -> dict:
        raw = self._get("/fundamentals", {"symbol": symbol, "exchange": exchange.value})
        try:
            return P1Fundamentals(**raw).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc

    def get_historical(self, symbol: str, exchange: Exchange, period_days: int = 252) -> list[dict]:
        raw = self._get("/historical", {"symbol": symbol, "exchange": exchange.value, "period": f"{period_days}d", "interval": "1d"})
        candles = raw.get("candles") if isinstance(raw, dict) else raw
        if not isinstance(candles, list):
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", "historical response missing candles")
        out: list[dict] = []
        for item in candles:
            try:
                out.append(P1HistoricalItem(**item).model_dump())
            except ValidationError as exc:
                raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc
        return out

    def get_market_status(self, exchange: Exchange) -> dict:
        raw = self._get("/market-status", {"exchange": exchange.value})
        try:
            return P1MarketStatus(**raw).model_dump()
        except ValidationError as exc:
            raise UpstreamError(self.source, "DATA_VALIDATION_FAILED", str(exc)) from exc

    def get_exchange_health(self) -> dict:
        out = {}
        for ex in [Exchange.NSE, Exchange.BSE, Exchange.NASDAQ]:
            try:
                status = self.get_market_status(ex)
                out[ex.value] = {"state": status.get("session") or ("OPEN" if status.get("is_open") else "CLOSED")}
            except UpstreamError:
                out[ex.value] = {"state": "UNKNOWN"}
        return out
