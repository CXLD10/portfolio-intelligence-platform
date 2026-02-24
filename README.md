# Project 3 — Portfolio Intelligence & Market Intelligence Platform

## Architecture Diagram

```text
Frontend (Next.js / UI)
        ↓
Project 3 FastAPI Orchestrator (this repo)
        ├── Intelligence Orchestrator
        ├── Portfolio Engine
        ├── Risk Engine
        ├── Backtest Engine
        ├── Sentiment Engine
        └── Market Engine
        ↓
Project 2 Quant + ML APIs (predictions/features/models)
        ↓
Project 1 Market Gateway APIs (quote/history/fundamentals/status)
```

## Code Layout

```text
app/
  api/v1/
    stock_intelligence.py
    portfolio.py
    backtesting.py
    sentiment.py
    market_overview.py
  services/
    intelligence_orchestrator.py
    portfolio_engine.py
    risk_engine.py
    backtest_engine.py
    sentiment_engine.py
    market_engine.py
    agent_reasoning_engine.py
  models/schemas.py
  integrations/
    project1_client.py
    project2_client.py
  utils/
    math_utils.py
    normalization.py
    validation.py
  config/settings.py
```

## Data Flow

1. API route validates params.
2. Route calls a service engine.
3. Engines fetch normalized upstream inputs via integrations.
4. Engines compute deterministic metrics and scores (numpy/pandas math).
5. Response models enforce contract and `schema_version: "1.0"`.
6. Standardized error handler returns:

```json
{
  "status": "error",
  "error_code": "HTTP_422",
  "message": "...",
  "schema_version": "1.0"
}
```

## Endpoint Catalog

- `GET /health`
- `GET /api/v1/intelligence?symbol=INFY&exchange=NSE`
- `POST /api/v1/portfolio/evaluate`
- `GET /api/v1/backtest?symbol=AAPL&exchange=NASDAQ&period=252`
- `GET /api/v1/sentiment?symbol=INFY&exchange=NSE`
- `GET /api/v1/market/overview`

## Integration Summary

- **Project 1 client** provides quote, historical candles, fundamentals, and exchange health.
- **Project 2 client** provides predictions and quant features.
- This repository orchestrates and computes portfolio/risk/backtest intelligence without re-training models.

## Example Responses

### Intelligence

```json
{
  "exchange": "NSE",
  "symbol": "INFY",
  "price": 412.3,
  "recommendation": "BUY",
  "confidence": 0.74,
  "expected_return": 0.031,
  "forecast_horizon": "5d",
  "risk_level": "Moderate",
  "quant_score": 0.69,
  "fundamental_score": 0.63,
  "sentiment_score": 0.58,
  "risk_score": 0.46,
  "drivers": ["Model probability supports upside scenario"],
  "warnings": [],
  "summary": "Recommendation=BUY; weighted composite=0.643; ...",
  "schema_version": "1.0"
}
```

### Portfolio Evaluate

```json
{
  "weights": {"AAPL": 0.6, "MSFT": 0.4},
  "expected_return": 0.021,
  "volatility": 0.187,
  "sharpe_ratio": 0.57,
  "var_95": 0.019,
  "max_drawdown_proxy": -0.134,
  "beta_vs_benchmark": 1.08,
  "concentration_index_hhi": 0.52,
  "sector_exposure": {"Technology": 1.0},
  "correlation_matrix": {"AAPL": {"AAPL": 1.0, "MSFT": 0.72}, "MSFT": {"AAPL": 0.72, "MSFT": 1.0}},
  "risk_contribution": {"AAPL": 0.48, "MSFT": 0.52},
  "schema_version": "1.0"
}
```

## Execution

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
pytest -q
```

## Cloud Run Notes

- Stateless API service, suitable for horizontal scaling.
- Deterministic per-symbol scoring avoids non-repeatable output behavior.
- Set container command to run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
