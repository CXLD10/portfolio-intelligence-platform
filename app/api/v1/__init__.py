from fastapi import APIRouter

from app.api.v1.backtesting import router as backtest_router
from app.api.v1.market_overview import router as market_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.sentiment import router as sentiment_router
from app.api.v1.stock_intelligence import router as intelligence_router

router = APIRouter()
router.include_router(intelligence_router)
router.include_router(portfolio_router)
router.include_router(backtest_router)
router.include_router(sentiment_router)
router.include_router(market_router)
