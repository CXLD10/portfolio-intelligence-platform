from __future__ import annotations

import hashlib

from app.models.schemas import Exchange


class Project2Client:
    """Deterministic adapter for P2-compatible quant APIs."""

    @staticmethod
    def _seed(symbol: str, exchange: Exchange) -> int:
        digest = hashlib.md5(f"{exchange.value}:{symbol}".encode()).hexdigest()[:8]
        return int(digest, 16)

    def get_prediction(self, symbol: str, exchange: Exchange) -> dict:
        seed = self._seed(symbol, exchange)
        p_up = 0.2 + (seed % 600) / 1000
        p_up = min(0.9, max(0.1, p_up))
        p_down = 1 - p_up
        if p_up > 0.58:
            pred = "BUY"
        elif p_down > 0.58:
            pred = "SELL"
        else:
            pred = "HOLD"
        return {
            "prediction": pred,
            "confidence": round(max(p_up, p_down), 4),
            "probability_up": round(p_up, 4),
            "probability_down": round(p_down, 4),
            "expected_return": round(-0.06 + (seed % 180) / 1000, 4),
            "risk_score": round(0.1 + (seed % 800) / 1000, 4),
            "forecast_horizon": "5d",
            "model_version": "v1",
        }

    def get_features(self, symbol: str, exchange: Exchange) -> dict:
        seed = self._seed(symbol, exchange)
        return {
            "volatility": round(0.1 + (seed % 350) / 1000, 4),
            "sharpe_ratio": round(-0.5 + (seed % 300) / 100, 4),
            "beta": round(0.4 + (seed % 160) / 100, 4),
            "drawdown": round(-0.45 + (seed % 250) / 1000, 4),
        }
