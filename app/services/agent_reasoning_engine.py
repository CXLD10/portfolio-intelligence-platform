from __future__ import annotations

from app.models.schemas import Recommendation
from app.utils.normalization import clamp


class AgentReasoningEngine:
    def compute(
        self,
        quant_score: float,
        fundamental_score: float,
        sentiment_score: float,
        risk_score: float,
    ) -> dict:
        weighted = 0.5 * quant_score + 0.3 * fundamental_score + 0.2 * sentiment_score
        adjusted = weighted - 0.35 * risk_score
        if adjusted >= 0.62:
            recommendation = Recommendation.BUY
        elif adjusted <= 0.42:
            recommendation = Recommendation.SELL
        else:
            recommendation = Recommendation.HOLD

        confidence = clamp(abs(adjusted - 0.5) * 2, 0, 1)
        risk_level = "High" if risk_score >= 0.7 else "Moderate" if risk_score >= 0.4 else "Low"

        drivers = []
        warnings = []
        if quant_score > 0.65:
            drivers.append("Model probability supports upside scenario")
        if fundamental_score > 0.6:
            drivers.append("Fundamental balance sheet and profitability profile is supportive")
        if sentiment_score > 0.55:
            drivers.append("Market sentiment trend is positive")
        if risk_score > 0.7:
            warnings.append("Elevated risk score from volatility and drawdown profile")
        if sentiment_score < 0.4:
            warnings.append("Negative sentiment divergence versus price")

        summary = (
            f"Recommendation={recommendation.value}; weighted composite={adjusted:.3f}; "
            f"quant={quant_score:.3f}, fundamental={fundamental_score:.3f}, sentiment={sentiment_score:.3f}, risk={risk_score:.3f}."
        )

        return {
            "recommendation": recommendation,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "drivers": drivers,
            "warnings": warnings,
            "summary": summary,
        }
