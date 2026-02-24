from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import BacktestResponse, Exchange
from app.services.backtest_engine import BacktestEngine
from app.utils.validation import require_non_empty

router = APIRouter()
engine = BacktestEngine()


@router.get("/backtest", response_model=BacktestResponse)
def backtest(
    symbol: str = Query(...),
    exchange: Exchange = Query(...),
    period: int = Query(default=252, ge=30, le=2000),
) -> BacktestResponse:
    require_non_empty(symbol, "symbol")
    return engine.run(symbol=symbol.upper(), exchange=exchange, period_days=period)
