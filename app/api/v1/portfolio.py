from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config.settings import settings
from app.models.schemas import PortfolioEvaluateRequest, PortfolioEvaluateResponse
from app.services.portfolio_engine import PortfolioEngine

router = APIRouter()
engine = PortfolioEngine()


@router.post("/portfolio/evaluate", response_model=PortfolioEvaluateResponse)
def evaluate_portfolio(request: PortfolioEvaluateRequest) -> PortfolioEvaluateResponse:
    if len(request.assets) > settings.max_portfolio_assets:
        raise HTTPException(status_code=422, detail=f"max portfolio size is {settings.max_portfolio_assets}")
    return engine.evaluate(request)
