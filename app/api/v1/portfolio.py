from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import PortfolioEvaluateRequest, PortfolioEvaluateResponse
from app.services.portfolio_engine import PortfolioEngine

router = APIRouter()
engine = PortfolioEngine()


@router.post("/portfolio/evaluate", response_model=PortfolioEvaluateResponse)
def evaluate_portfolio(request: PortfolioEvaluateRequest) -> PortfolioEvaluateResponse:
    return engine.evaluate(request)
