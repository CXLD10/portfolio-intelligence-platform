from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib

from app.models.schemas import Exchange


class Project1Client:
    """Deterministic adapter for P1-compatible data contracts."""

    @staticmethod
    def _seed(symbol: str, exchange: Exchange) -> int:
        digest = hashlib.sha256(f"{exchange.value}:{symbol}".encode()).hexdigest()[:8]
        return int(digest, 16)

    def get_quote(self, symbol: str, exchange: Exchange) -> dict:
        seed = self._seed(symbol, exchange)
        price = 50 + (seed % 5000) / 10
        volume = 100000 + (seed % 7000000)
        currency = "INR" if exchange in {Exchange.NSE, Exchange.BSE} else "USD"
        return {
            "symbol": symbol,
            "exchange": exchange.value,
            "price": round(price, 2),
            "volume": float(volume),
            "currency": currency,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def get_historical(self, symbol: str, exchange: Exchange, period_days: int = 252) -> list[dict]:
        seed = self._seed(symbol, exchange)
        now = datetime.now(UTC)
        base = 80 + (seed % 4000) / 20
        drift = ((seed % 17) - 8) / 10000
        series: list[dict] = []
        px = base
        for i in range(period_days):
            wave = ((i % 11) - 5) / 1000
            px = max(1.0, px * (1 + drift + wave))
            series.append({
                "timestamp": (now - timedelta(days=(period_days - i))).isoformat(),
                "close": round(px, 4),
            })
        return series

    def get_fundamentals(self, symbol: str, exchange: Exchange) -> dict:
        seed = self._seed(symbol, exchange)
        sectors = ["Technology", "Financials", "Healthcare", "Industrials", "Energy"]
        industries = ["Software", "Banks", "Biotech", "Manufacturing", "Oil & Gas"]
        idx = seed % len(sectors)
        return {
            "market_cap": float(1e9 + (seed % 1000) * 1e8),
            "sector": sectors[idx],
            "industry": industries[idx],
            "debt_to_equity": round((seed % 190) / 100, 3),
            "roe": round(0.05 + (seed % 30) / 100, 3),
            "revenue_growth": round(-0.05 + (seed % 50) / 100, 3),
        }

    def get_exchange_health(self) -> dict:
        return {
            "NSE": {"state": "CLOSED", "failure_rate": 0.02, "average_latency_ms": 82.0},
            "BSE": {"state": "CLOSED", "failure_rate": 0.03, "average_latency_ms": 88.0},
            "NASDAQ": {"state": "OPEN", "failure_rate": 0.01, "average_latency_ms": 76.0},
        }
