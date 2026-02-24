from __future__ import annotations

from fastapi import APIRouter, Query

from app.models.schemas import Exchange, SentimentResponse
from app.services.sentiment_engine import SentimentEngine

router = APIRouter()
engine = SentimentEngine()


@router.get("/sentiment", response_model=SentimentResponse)
def get_sentiment(symbol: str = Query(...), exchange: Exchange = Query(...)) -> SentimentResponse:
    return engine.compute(symbol=symbol.upper(), exchange=exchange)
