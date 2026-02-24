from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_intelligence_endpoint() -> None:
    r = client.get("/api/v1/intelligence", params={"symbol": "INFY", "exchange": "NSE"})
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == "1.0"
    assert body["recommendation"] in {"BUY", "HOLD", "SELL"}
    assert set(["quant_score", "fundamental_score", "sentiment_score", "risk_score"]).issubset(set(body))


def test_portfolio_evaluate_manual_mode() -> None:
    payload = {
        "assets": [
            {"symbol": "AAPL", "exchange": "NASDAQ", "weight": 0.7},
            {"symbol": "MSFT", "exchange": "NASDAQ", "weight": 0.3},
        ],
        "weighting_mode": "manual",
    }
    r = client.post("/api/v1/portfolio/evaluate", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert abs(sum(body["weights"].values()) - 1.0) < 1e-8
    assert "correlation_matrix" in body


def test_backtest_endpoint() -> None:
    r = client.get("/api/v1/backtest", params={"symbol": "AAPL", "exchange": "NASDAQ", "period": 252})
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == "1.0"
    assert isinstance(body["trade_log"], list)


def test_sentiment_endpoint() -> None:
    r = client.get("/api/v1/sentiment", params={"symbol": "INFY", "exchange": "NSE"})
    assert r.status_code == 200
    body = r.json()
    assert body["bullish_ratio"] + body["bearish_ratio"] == 1


def test_market_overview() -> None:
    r = client.get("/api/v1/market/overview")
    assert r.status_code == 200
    body = r.json()
    assert "exchange_health" in body
