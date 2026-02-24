from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_intelligence_endpoint_includes_provenance_and_confidence() -> None:
    r = client.get("/api/v1/intelligence", params={"symbol": "INFY", "exchange": "NSE"})
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == "1.0"
    assert body["recommendation"] in {"BUY", "HOLD", "SELL"}
    assert "provenance" in body
    assert "confidence_diagnostics" in body
    assert "benchmark" in body


def test_portfolio_evaluate_includes_stress_tests() -> None:
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
    assert len(body["stress_tests"]) == 4


def test_backtest_endpoint() -> None:
    r = client.get("/api/v1/backtest", params={"symbol": "AAPL", "exchange": "NASDAQ", "period": 252})
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == "1.0"
    assert body["benchmark_symbol"] == "SP500"


def test_metrics_endpoint() -> None:
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "request_count" in r.json()
