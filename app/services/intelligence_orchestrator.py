from __future__ import annotations

from app.config.settings import settings
from app.integrations.project1_client import Project1Client
from app.integrations.project2_client import Project2Client
from app.models.schemas import Exchange, IntelligenceResponse
from app.services.agent_reasoning_engine import AgentReasoningEngine
from app.services.sentiment_engine import SentimentEngine
from app.utils.normalization import clamp, normalize_symbol
from app.utils.validation import filter_valid_numeric_map


class IntelligenceOrchestrator:
    def __init__(self) -> None:
        self.p1 = Project1Client()
        self.p2 = Project2Client()
        self.sentiment = SentimentEngine()
        self.reasoning = AgentReasoningEngine()

    def _fundamental_score(self, fundamentals: dict[str, float | str]) -> float:
        numeric = filter_valid_numeric_map(
            {
                "roe": fundamentals.get("roe"),
                "revenue_growth": fundamentals.get("revenue_growth"),
                "debt_to_equity": fundamentals.get("debt_to_equity"),
            }
        )
        roe = numeric.get("roe", 0.05)
        rev = numeric.get("revenue_growth", 0)
        debt = numeric.get("debt_to_equity", 1)
        score = 0.5 * clamp(roe / 0.25, 0, 1) + 0.35 * clamp((rev + 0.1) / 0.4, 0, 1) + 0.15 * (1 - clamp(debt / 2, 0, 1))
        return round(clamp(score, 0, 1), 4)

    def _quant_score(self, prediction: dict[str, float], features: dict[str, float]) -> float:
        conf = float(prediction.get("confidence", 0.5))
        expected = float(prediction.get("expected_return", 0))
        vol = float(features.get("volatility", 0.3))
        dd = abs(float(features.get("drawdown", -0.2)))
        score = 0.45 * conf + 0.3 * clamp((expected + 0.1) / 0.2, 0, 1) + 0.25 * (1 - clamp((vol + dd) / 1.2, 0, 1))
        return round(clamp(score, 0, 1), 4)

    def _risk_score(self, prediction: dict[str, float], features: dict[str, float]) -> float:
        model_risk = float(prediction.get("risk_score", 0.5))
        vol = float(features.get("volatility", 0.2))
        dd = abs(float(features.get("drawdown", -0.2)))
        score = 0.5 * model_risk + 0.3 * clamp(vol / 0.8, 0, 1) + 0.2 * clamp(dd / 0.5, 0, 1)
        return round(clamp(score, 0, 1), 4)

    def run(self, symbol: str, exchange: Exchange) -> IntelligenceResponse:
        symbol = normalize_symbol(symbol)
        quote = self.p1.get_quote(symbol, exchange)
        fundamentals = self.p1.get_fundamentals(symbol, exchange)
        prediction = self.p2.get_prediction(symbol, exchange)
        features = self.p2.get_features(symbol, exchange)
        sent = self.sentiment.compute(symbol, exchange)

        quant = self._quant_score(prediction, features)
        fundamental = self._fundamental_score(fundamentals)
        risk = self._risk_score(prediction, features)
        sentiment = clamp((sent.sentiment_score + 1) / 2, 0, 1)
        reasoned = self.reasoning.compute(quant, fundamental, sentiment, risk)

        return IntelligenceResponse(
            exchange=exchange,
            symbol=symbol,
            price=float(quote["price"]),
            recommendation=reasoned["recommendation"],
            confidence=reasoned["confidence"],
            expected_return=float(prediction["expected_return"]),
            forecast_horizon=str(prediction["forecast_horizon"]),
            risk_level=reasoned["risk_level"],
            quant_score=quant,
            fundamental_score=fundamental,
            sentiment_score=round(sentiment, 4),
            risk_score=risk,
            drivers=reasoned["drivers"],
            warnings=reasoned["warnings"],
            summary=reasoned["summary"],
            schema_version=settings.schema_version,
        )
