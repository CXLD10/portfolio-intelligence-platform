from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import Exchange, IntelligenceResponse
from app.services.intelligence_orchestrator import IntelligenceOrchestrator
from app.utils.validation import require_non_empty

router = APIRouter()
orchestrator = IntelligenceOrchestrator()


@router.get("/intelligence", response_model=IntelligenceResponse)
def get_intelligence(symbol: str = Query(...), exchange: Exchange = Query(...)) -> IntelligenceResponse:
    require_non_empty(symbol, "symbol")
    return orchestrator.run(symbol=symbol, exchange=exchange)
