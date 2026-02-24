import numpy as np

from app.integrations.project1_client import Project1Client
from app.models.schemas import Exchange, PortfolioEvaluateRequest
from app.services.intelligence_orchestrator import IntelligenceOrchestrator
from app.services.portfolio_engine import PortfolioEngine
from app.services.risk_engine import RiskEngine
from app.utils.math_utils import returns_from_prices


def test_correlation_computation() -> None:
    risk = RiskEngine()
    corr = risk.correlation({"A": [0.1, 0.2, 0.3], "B": [0.1, 0.2, 0.3]})
    assert corr["A"]["B"] == 1.0


def test_portfolio_math_correctness() -> None:
    engine = PortfolioEngine()
    req = PortfolioEvaluateRequest(
        assets=[
            {"symbol": "AAPL", "exchange": "NASDAQ", "weight": 0.5},
            {"symbol": "MSFT", "exchange": "NASDAQ", "weight": 0.5},
        ],
        weighting_mode="manual",
    )
    out = engine.evaluate(req)
    assert abs(sum(out.weights.values()) - 1.0) < 1e-8
    assert out.volatility >= 0


def test_risk_metrics_var_and_beta() -> None:
    p1 = Project1Client()
    risk = RiskEngine()
    a = returns_from_prices([x["close"] for x in p1.get_historical("AAPL", Exchange.NASDAQ, 260)])
    b = returns_from_prices([x["close"] for x in p1.get_historical("SPY", Exchange.NASDAQ, 260)])
    beta = risk.beta(a, b)
    var = risk.var95(float(np.std(a) * np.sqrt(252)))
    assert isinstance(beta, float)
    assert var >= 0


def test_composite_scoring_range() -> None:
    orchestrator = IntelligenceOrchestrator()
    out = orchestrator.run("INFY", Exchange.NSE)
    assert 0 <= out.quant_score <= 1
    assert 0 <= out.fundamental_score <= 1
    assert 0 <= out.sentiment_score <= 1
    assert 0 <= out.risk_score <= 1


def test_intelligence_orchestration_determinism() -> None:
    orchestrator = IntelligenceOrchestrator()
    a = orchestrator.run("INFY", Exchange.NSE)
    b = orchestrator.run("INFY", Exchange.NSE)
    # price is deterministic; timestamp is not part of output
    assert a.price == b.price
    assert a.recommendation == b.recommendation
