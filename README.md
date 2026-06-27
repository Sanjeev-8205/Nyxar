# Nyxar — AI Inference and Observability Platform

Nyxar is an AI Inference & Observability Platform that combines multi-model sentiment inference, batch analytics, LLM-generated insights, and operational monitoring. A Streamlit frontend provides live inference, batch processing, AI reports, and platform observability, while a FastAPI backend handles model execution, telemetry collection, AI-powered analysis, and data persistence.

---

## Key Highlights

- Three ML models with different runtime backends (scikit-learn, TensorFlow/Keras, ONNX Runtime)
- Batch inference pipeline with background job tracking, progress polling, and buffered DB writes
- LLM-powered summaries via Gemini with Groq fallback — three report depths
- Real-time drift detection across confidence, sentiment, and input length
- API key authentication on all endpoints via constant-time `secrets.compare_digest`
- Structured JSON logging via `structlog` with per-request `request_id` tracing
- Prometheus metrics with HTTP Basic Auth for Grafana scraping
- Tag-based CI/CD pipeline — deploys triggered by `v*` tags or manual dispatch
- Fully containerized backend on Hugging Face Spaces (CPU-only)
- Models stored on Hugging Face Hub, downloaded at startup via `snapshot_download`

---

## Architecture Diagram

```
┌──────────────────────────────────────────┐        ┌──────────────────────────────────────────┐
│               Streamlit UI               │        │             FastAPI Backend              │
│            (Streamlit Cloud)             │        │          (Hugging Face Spaces)           │
│                                          │        │                                          │
│  ┌────────────────┐  ┌────────────────┐  │        │  ┌────────────────┐  ┌────────────────┐  │
│  │    Overview    │  │ Live Inference │  │        │  │    /predict    │  │   /batch/*     │  │
│  └────────────────┘  └────────────────┘  │  HTTP  │  └────────────────┘  └────────────────┘  │
│  ┌────────────────┐  ┌────────────────┐  │◄──────►│  ┌────────────────┐  ┌────────────────┐  │
│  │     Batch      │  │   AI Intel.    │  │        │  │   /dashboard   │  │   /prometheus  │  │
│  │  Intelligence  │  │    Reports     │  │        │  └────────────────┘  │    _metrics    │  │
│  └────────────────┘  └────────────────┘  │        │                      └────────┬───────┘  │
│  ┌────────────────┐                      │        └───────────────────┬───────────|──────────┘
│  │ Observability  │                      │                            │           │
│  │   Dashboards   │                      │                            │           │ Scraped by
│  └────────────────┘                      │                            │           ▼
└──────────────────────────────────────────┘                            │   ┌───────────────┐
                                                                        │   │  Prometheus   │
                                                                        │   └───────┬───────┘
                                                                        │           │ Queried by
                                                                        │           ▼
                                                                        │   ┌───────────────┐
                                                                        │   │    Grafana    │
                                                                        │   └───────────────┘
         ┌──────────────────────────────┬──────────────────────────────┬┘
         │                              │                              │
         ▼                              ▼                              ▼
┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
│  Neon Postgres  │            │ HuggingFace Hub │            │   Gemini/Groq   │
│   (us-east-1)   │            │ (Model Storage) │            │    LLM APIs     │
│                 │            │                 │            │                 │
│ ─ Inference Logs│            │ ─ LogReg Asset  │            │ ─ Gemini Flash  │
│ ─ Batch Jobs/Res│            │ ─ Bi-LSTM Asset │            │   Lite (Primary)│
│ ─ AI Reports    │            │ ─ RoBERTa Asset │            │ ─ Groq Llama    │
│ ─ Insights      │            │                 │            │   (Fallback)    │
└─────────────────┘            └─────────────────┘            └─────────────────┘
```

---

## Real-Time Inference Workflow

```
User submits text
       │
       ▼
POST /predict  (X-Api-Key header required)
       │
       ├── API key verification (secrets.compare_digest)
       ├── Request ID assigned (LoggingMiddleware)
       ├── Input validation
       ├── Text preprocessing (model-specific)
       ├── Model inference (sklearn / Keras / ONNX)
       ├── Confidence scoring + certainty classification
       ├── LLM insight generation (Gemini → Groq fallback)
       ├── Log to PostgreSQL (background task, carries request_id)
       ├── Prometheus metrics updated
       │
       ▼
Response: prediction, confidence scores, latency, execution trace, insight
```

All log lines for a request share the same `request_id`, including the background DB write that runs after the response is sent.

---

## Batch Processing Workflow

```
CSV upload via POST /batch/upload  (X-Api-Key header required)
       │
       ├── API key verification
       ├── CSV validation (structure + column check)
       ├── BatchJob record created (status: pending)
       └── Background task dispatched
              │
              ├── predict_batch() — full dataset inference
              ├── Results buffered → bulk INSERT every N rows
              ├── Progress tracked in BatchJob (processed_rows, progress %)
              └── On completion: throughput, timing breakdown, AI insights saved, Prometheus metrics updated
                     │
                     ▼
              GET /batch/job/{id} — poll for status
              GET /batch/job/{id}/results — fetch predictions
              GET /batch/job/{id}/summary — generate LLM report
```

---

## Feature Overview

| Feature | Description |
|---|---|
| Live Inference | Single-text prediction with confidence scores, execution trace, and LLM insight |
| Batch Processing | CSV upload → background inference → buffered writes → results retrieval |
| AI Reports | LLM-generated reports (Executive / Detailed / Full) from batch results |
| Overview Dashboard | System KPIs, latency trends, throughput, LLM-generated operational insights |
| Observability | Sentiment distribution, model usage, drift indicators, confidence tracking |
| Infrastructure Health | CPU/RAM usage, DB connectivity, model load status, uptime |
| Prometheus Metrics | Counters, histograms, gauges for inference, batch, and LLM operations |
| Platform Status | Composite health score across failure rate, latency shift, CPU, drift signals |
| API Authentication | Constant-time API key verification on all endpoints except `/health` |
| Structured Logging | JSON logs via structlog with `request_id`, `model`, `duration_ms` per request |

---

## Model Comparison

| Model | Runtime | Accuracy | Primary Tradeoff |
|---|---|---|---|
| Logistic Regression | scikit-learn | 69.3% | Fastest inference |
| Bi-LSTM | TensorFlow/Keras | 72.8% | Accuracy vs latency balance |
| RoBERTa Transformer | ONNX Runtime (INT8) | 77.6% | Highest accuracy |

All metrics sourced from `metrics/*.json`, evaluated on a held-out test set.

---

## Repository Structure

```
├── app/
│   ├── core/               # Model loader, registry, preprocessing, DB, metrics
│   │   ├── logging_config.py       # structlog setup — called once at lifespan startup
│   │   ├── security.py             # verify_api_key dependency (secrets.compare_digest)
│   │   └── settings.py             # Pydantic BaseSettings with lru_cache
│   ├── middleware/
│   │   └── logging_middleware.py   # Request ID generation + request/response logging
│   ├── routes/             # FastAPI route handlers
│   ├── schemas/            # Pydantic request models
│   └── services/
│       ├── ml_service.py           # Single and batch inference logic
│       ├── batch_service.py        # Background batch job execution
│       ├── llm_service.py          # LLM summary generation
│       ├── logging_service.py      # Inference log persistence
│       ├── insights_service/       # Live insights, overview insights, platform status
│       └── metrics_service/        # Dashboard, analytics, health, drift metrics
├── models/                 # SQLAlchemy ORM models
├── metrics/                # Stored ML model evaluation JSON files
├── ui/                     # Streamlit frontend (separate deployment)
│   ├── ui.py               # Main application, all page rendering
│   ├── components.py       # Reusable HTML/CSS component functions
│   └── styles.py           # Global CSS injection
├── tests/                  # pytest test suite
├── Dockerfile              # Backend container definition
├── requirements.txt        # Full dependency list
├── requirements-ci.txt     # CI-only dependencies (ML packages stripped)
├── requirements-test.txt   # Test-only dependencies
├── evaluate.py             # Offline model evaluation script
└── docs/                   # Architecture and engineering documentation
```

---

## Documentation Index

| Document | Contents |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System topology, request lifecycle, model runtime, concurrency |
| [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) | Prometheus metrics, structured logging, drift detection, platform health |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Hugging Face Spaces, CI/CD pipeline, environment variables, security |
| [docs/ENGINEERING_DECISIONS.md](docs/ENGINEERING_DECISIONS.md) | Architectural tradeoffs and technology choices |

---

## Quick Start

**Backend (local):**
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

**Frontend (local):**
```bash
cd ui
pip install -r requirements.txt
streamlit run ui.py
```

Set `BASE_URL` in `ui/ui.py` to point at your backend instance.

**Required environment variables:**
```
DATABASE_URL=
GEMINI_API_KEY=
GROQ_API_KEY=
PROMETHEUS_METRICS_USERNAME=
PROMETHEUS_METRICS_PASSWORD=
PROTECT_API_KEY=
```

---

## CI/CD

Deploys are triggered by pushing a `v*` tag or via manual workflow dispatch in GitHub Actions. Regular pushes to `main` run tests only — no automatic deploy.

```bash
# to deploy
git tag v1.1.0
git push origin v1.1.0
```

The pipeline runs the full test suite before deploying. A failing test blocks the deploy.

---

## Future Improvements

- Alembic schema migrations — versioned, reversible schema changes as the data model evolves
- Grafana Loki integration — ship structlog JSON to Loki for queryable, alertable log dashboards correlated with Prometheus metrics
- Per-model latency SLO monitoring — Grafana alert rules on p95 histograms already collected
- Model confidence calibration — reliability diagrams to validate whether confidence scores reflect true accuracy
- Drift alerting — Grafana alerts when confidence or sentiment distribution shifts beyond threshold
- Server-Sent Events for AI reports — replace polling loop with push-based report delivery
- Request rate limiting — sliding window protection on inference and LLM endpoints

---

## License

MIT