import numpy as np

from app.integrations.project1_client import Project1Client
from app.models.schemas import Exchange, PortfolioEvaluateRequest
from app.services.benchmark_engine import BenchmarkEngine
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
    b = returns_from_prices([x["close"] for x in p1.get_historical("SP500", Exchange.NASDAQ, 260)])
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
    assert 0 <= out.composite_score <= 1


def test_benchmark_metrics_shape() -> None:
    p1 = Project1Client()
    b = BenchmarkEngine()
    ar = returns_from_prices([x["close"] for x in p1.get_historical("AAPL", Exchange.NASDAQ, 260)])
    br = returns_from_prices([x["close"] for x in p1.get_historical("SP500", Exchange.NASDAQ, 260)])
    out = b.compare(ar, br, "SP500")
    assert set(["active_return", "tracking_error", "information_ratio", "relative_drawdown"]).issubset(set(out.keys()))
