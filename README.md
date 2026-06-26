# Nyxar — AI Inference and Observability Platform

Nyxar is an AI Inference & Observability Platform that combines multi-model sentiment inference, batch analytics, LLM-generated insights, and operational monitoring. A Streamlit frontend provides live inference, batch processing, AI intelligence reports, and platform observability, while a FastAPI backend handles model execution, telemetry collection, AI-powered analysis, and data persistence.

---

## Key Highlights

- Three ML models with different runtime backends (scikit-learn, TensorFlow/Keras, ONNX Runtime)
- Batch inference pipeline with background job tracking, progress polling, and buffered DB writes
- LLM-powered summaries via Gemini with Groq fallback — three report depths
- Real-time drift detection across confidence, sentiment, and input length
- Prometheus metrics with HTTP Basic Auth for Grafana scraping
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
POST /predict
       │
       ├── Input Validation
       ├── Text preprocessing (model-specific)
       ├── Model inference (sklearn / Keras / ONNX)
       ├── Confidence scoring + certainty classification
       ├── LLM insight generation (Gemini → Groq fallback)
       ├── Log to PostgreSQL
       ├── Prometheus metrics updated
       │
       ▼
Response: prediction, confidence scores, latency, execution trace, insight
```

---

## Batch Processing Workflow

```
CSV upload via POST /batch/upload
       │
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
| AI Intelligence | LLM-generated reports (Executive / Detailed / Full) from batch results |
| Overview Dashboard | System KPIs, latency trends, throughput, LLM-generated operational insights |
| Observability | Sentiment distribution, model usage, drift indicators, confidence tracking |
| Infrastructure Health | CPU/RAM usage, DB connectivity, model load status, uptime |
| Prometheus Metrics | Counters, histograms, gauges for inference, batch, and LLM operations |
| Platform Status | Composite health score across failure rate, latency shift, CPU, drift signals |

---

## Model Comparison

| Model | Runtime | Accuracy | Primary Tradeoff |
|---|---|---|---|
| Logistic Regression | scikit-learn | 69.3% | Fastest Inference |
| Bi-LSTM | TensorFlow/Keras | 72.8% | Accuracy vs Latency balance |
| RoBERTa Transformer | ONNX Runtime (INT8) | 77.6% | Highest accuracy |

All metrics sourced from `metrics/*.json`, evaluated on a held-out test set.

---

## Repository Structure

```
├── app/
│   ├── core/               # Model loader, registry, preprocessing, DB, metrics
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
├── metrics/                # Stored ml model evaluation JSON files
├── ui/                     # Streamlit frontend (separate deployment)
│   ├── ui.py               # Main application, all page rendering
│   ├── components.py       # Reusable HTML/CSS component functions
│   └── styles.py           # Global CSS injection
├── Dockerfile              # Backend container definition
├── evaluate.py             # Offline model evaluation script
└── docs/                   # Architecture and engineering documentation
```

---

## Documentation Index

| Document | Contents |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System topology, request lifecycle, model runtime, concurrency |
| [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) | Prometheus metrics, drift detection, platform health scoring |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Hugging Face Spaces, model storage, environment variables |
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
```

---

## Future Improvements

- JWT/API-key authentication
- Alembic schema migrations
- Per-model latency SLO monitoring
- Server-Sent Events for long-running AI reports
- Request rate limiting and quota controls

---

## License

MIT
