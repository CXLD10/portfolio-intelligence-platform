from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import MarketOverviewResponse
from app.services.market_engine import MarketEngine

router = APIRouter()
engine = MarketEngine()


@router.get("/market/overview", response_model=MarketOverviewResponse)
def market_overview() -> MarketOverviewResponse:
    return engine.overview()
