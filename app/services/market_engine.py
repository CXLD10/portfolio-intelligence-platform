from __future__ import annotations

from app.config.settings import settings
from app.integrations.project1_client import Project1Client
from app.models.schemas import Exchange, MarketOverviewResponse


class MarketEngine:
    def __init__(self) -> None:
        self.p1 = Project1Client()

    def overview(self) -> MarketOverviewResponse:
        sectors = {
            "Technology": 1.3,
            "Financials": -0.4,
            "Healthcare": 0.8,
            "Energy": -1.1,
            "Industrials": 0.2,
        }
        top_gainers = [
            {"symbol": "NVDA", "exchange": "NASDAQ", "change_pct": 2.1},
            {"symbol": "INFY", "exchange": "NSE", "change_pct": 1.7},
            {"symbol": "RELIANCE", "exchange": "BSE", "change_pct": 1.4},
        ]
        top_losers = [
            {"symbol": "TSLA", "exchange": "NASDAQ", "change_pct": -2.0},
            {"symbol": "HDFCBANK", "exchange": "NSE", "change_pct": -1.3},
            {"symbol": "TCS", "exchange": "BSE", "change_pct": -1.1},
        ]
        vol = {
            Exchange.NSE.value: 0.21,
            Exchange.BSE.value: 0.22,
            Exchange.NASDAQ.value: 0.27,
        }
        return MarketOverviewResponse(
            sector_performance=sectors,
            market_cap_distribution={"large_cap": 1250, "mid_cap": 2700, "small_cap": 5400},
            top_gainers=top_gainers,
            top_losers=top_losers,
            volatility_snapshot=vol,
            exchange_health=self.p1.get_exchange_health(),
            schema_version=settings.schema_version,
        )
