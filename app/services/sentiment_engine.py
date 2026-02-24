from __future__ import annotations

import hashlib

from app.models.schemas import Exchange, SentimentResponse
from app.config.settings import settings
from app.utils.normalization import clamp


class SentimentEngine:
    @staticmethod
    def _seed(symbol: str, exchange: Exchange) -> int:
        return int(hashlib.sha1(f"{exchange.value}:{symbol}".encode()).hexdigest()[:8], 16)

    def compute(self, symbol: str, exchange: Exchange) -> SentimentResponse:
        seed = self._seed(symbol, exchange)
        score = -1 + (seed % 200) / 100
        bullish = clamp(0.5 + score / 2, 0, 1)
        bearish = 1 - bullish
        momentum = ((seed % 40) - 20) / 100
        divergence = ((seed % 120) - 60) / 100
        trend = [round(clamp(score + (i - 3) * 0.04, -1, 1), 4) for i in range(7)]
        return SentimentResponse(
            symbol=symbol,
            exchange=exchange,
            sentiment_score=round(score, 4),
            bullish_ratio=round(bullish, 4),
            bearish_ratio=round(bearish, 4),
            momentum=round(momentum, 4),
            divergence_vs_price=round(divergence, 4),
            sentiment_trend=trend,
            schema_version=settings.schema_version,
        )
