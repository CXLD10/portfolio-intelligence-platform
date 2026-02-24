# Portfolio Intelligence Platform

## System Architecture

```text
┌──────────────────────────┐
│ Next.js Frontend (Cloud) │
└────────────┬─────────────┘
             │ NEXT_PUBLIC_API_URL
┌────────────▼─────────────┐
│ FastAPI Orchestrator     │
│ - Intelligence Engine    │
│ - Portfolio + Risk       │
│ - Backtest + Sentiment   │
│ - Benchmark + Stress     │
│ - Metrics + Caching      │
└───────┬─────────┬────────┘
        │         │
┌───────▼───┐ ┌───▼────────┐
│ Project 1 │ │ Project 2  │
│ Market API│ │ Quant API  │
└───────────┘ └────────────┘
```

## Data Flow

1. Request enters FastAPI with request-size and rate-limit guards.
2. Middleware captures latency and counters for observability.
3. Service layer fetches upstream Project 1/Project 2 inputs.
4. Deterministic analytics compute scores, confidence calibration, benchmark metrics, and stress scenarios.
5. Response is cached (short TTL for intelligence/portfolio endpoints).
6. Response envelope includes `schema_version: "1.0"`.

## API Catalog

- `GET /health`
- `GET /metrics`
- `GET /api/v1/intelligence?symbol=INFY&exchange=NSE`
- `POST /api/v1/portfolio/evaluate`
- `GET /api/v1/backtest?symbol=AAPL&exchange=NASDAQ&period=252`
- `GET /api/v1/sentiment?symbol=INFY&exchange=NSE`
- `GET /api/v1/market/overview`

### Intelligence Response Additions

- model provenance: `model_version`, `feature_schema_version`, `prediction_generated_at`, `forecast_horizon_days`, `upstream_latency_ms`
- score transparency: component scores, `composite_score`, score weights, formula version
- confidence diagnostics: raw + calibrated confidence, disagreement index, stability score, decay factor
- benchmark metrics: active return, tracking error, information ratio, relative drawdown
- explainability metadata: feature importance and directional drivers
- regime labels: market regime + volatility regime

## Frontend (Next.js)

`frontend/` contains an App Router TypeScript UI with a dark, minimal institutional layout:

- `/dashboard`
- `/intelligence`
- `/portfolio`
- `/backtest`
- `/sentiment`

Environment variable:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## UI Screenshots

- Dashboard placeholder: `docs/screenshots/dashboard.png`
- Intelligence placeholder: `docs/screenshots/intelligence.png`
- Portfolio placeholder: `docs/screenshots/portfolio.png`

## Local Run

```bash
# backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# frontend
cd frontend
npm install
npm run dev
```

## Google Cloud Deployment (Cost Optimized)

### Prerequisites

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com iam.googleapis.com
```

### Service account

```bash
gcloud iam service-accounts create pip-runtime-sa --display-name="PIP Runtime"
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:pip-runtime-sa@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### Artifact Registry

```bash
gcloud artifacts repositories create pip-repo --repository-format=docker --location=us-central1
```

### Backend container (Cloud Run)

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/<PROJECT_ID>/pip-repo/pip-backend:latest

gcloud run deploy pip-backend \
  --image us-central1-docker.pkg.dev/<PROJECT_ID>/pip-repo/pip-backend:latest \
  --region us-central1 \
  --platform managed \
  --service-account pip-runtime-sa@<PROJECT_ID>.iam.gserviceaccount.com \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --concurrency 80 \
  --allow-unauthenticated
```

### Frontend container (Cloud Run)

```bash
gcloud builds submit ./frontend --tag us-central1-docker.pkg.dev/<PROJECT_ID>/pip-repo/pip-frontend:latest

gcloud run deploy pip-frontend \
  --image us-central1-docker.pkg.dev/<PROJECT_ID>/pip-repo/pip-frontend:latest \
  --region us-central1 \
  --platform managed \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars NEXT_PUBLIC_API_URL=https://pip-backend-<hash>-uc.a.run.app \
  --allow-unauthenticated
```

### Optional domain mapping

```bash
gcloud run domain-mappings create --service pip-frontend --domain <YOUR_DOMAIN> --region us-central1
```

## Scaling + Cost Strategy

- Cloud Run scale-to-zero (`min-instances=0`).
- No always-on databases.
- No Pub/Sub workers.
- CPU allocated during request only.
- Small memory footprint (`256Mi`) and `max-instances=2`.
- Stateless API and frontend services.
