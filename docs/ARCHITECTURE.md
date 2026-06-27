# Architecture

## System Topology

Nyxar is split into two independently deployed services that communicate exclusively over HTTP.

```
┌──────────────────────────┐          ┌──────────────────────────────────────────┐
│     Streamlit Frontend   │          │           FastAPI Backend                │
│     (Streamlit Cloud)    │          │        (Hugging Face Spaces)             │
│                          │          │                                          │
│  All UI rendering        │◄──HTTP──►│  All ML inference, storage, metrics      │
│  All state management    │          │  All LLM calls                           │
│  No ML logic             │          │  No UI rendering                         │
└──────────────────────────┘          └─────────────┬────────────────────────────┘
                                                    │
                               ┌────────────────────┼────────────────────┐
                               │                    │                    │
                    ┌──────────▼──────┐  ┌──────────▼──────┐  ┌──────────▼──────┐
                    │  Neon Postgres  │  │  HF Hub Models  │  │  Gemini / Groq  │
                    └─────────────────┘  └─────────────────┘  └─────────────────┘
```

The frontend holds no ML logic and makes no direct database connections. Every piece of persistent state flows through the API. All API requests (except `/health`) require a valid `X-Api-Key` header.

---

## Request Lifecycle — Live Inference

```
POST /predict
  │
  ├─ API key verification (verify_api_key dependency, secrets.compare_digest)
  ├─ LoggingMiddleware assigns request_id, logs request_started
  ├─ Input validation (empty text check) → warning logged if invalid
  ├─ get_model(name) — returns cached pipeline from loaded_models dict
  ├─ Model-specific preprocessing → debug logs per stage
  ├─ Inference → prediction + probability array → info log with duration_ms
  ├─ Low confidence check → warning logged if confidence < 0.5
  ├─ Confidence scoring + certainty label
  ├─ LLM insight generation (Gemini → Groq fallback)
  ├─ Prometheus counters + histograms updated
  ├─ request_id extracted from contextvars
  ├─ DB write dispatched as background task (carries request_id manually)
  └─ Response returned
  │
  └─ [background] log_predictions() → inference_result_saved or inference_db_write_failed
```

Background tasks run after the response is sent and outside the request's `contextvars` context. The `request_id` is extracted before the response is returned and passed explicitly to the background task, so the DB write log can be correlated with the inference log in HF Spaces output.

Timing breakdown (trace) is captured per pipeline stage and returned to the client.

---

## Request Lifecycle — Batch Inference

Batch jobs are asynchronous. The upload endpoint validates, persists a job record, and dispatches a background task. The client polls for status.

```
POST /batch/upload
  │
  ├─ API key verification
  ├─ CSV format and column validation
  ├─ File written to /app/upload/
  ├─ BatchJob record created (status: pending)
  ├─ Background task dispatched via FastAPI BackgroundTasks
  └─ job_id returned immediately

Background task (process_batch_job):
  │
  ├─ predict_batch() — full dataset inference
  │    ├─ Logistic: preprocess → TF-IDF → predict_proba
  │    ├─ Bi-LSTM: preprocess → tokenize → pad → model.predict
  │    └─ RoBERTa: preprocess → tokenize → ONNX session.run (batched, size 64)
  │
  ├─ Results accumulated in a buffer
  ├─ Bulk INSERT every max(1, total_rows // 10) rows
  ├─ BatchJob.progress updated per buffer flush
  ├─ On completion: timing fields, throughput, AI insights saved
  └─ Prometheus batch metrics recorded

GET /batch/job/{id}           — returns job status, progress, timing breakdown
GET /batch/job/{id}/results   — returns all predictions
GET /batch/job/{id}/summary   — triggers or retrieves LLM report
```

The buffer size is dynamically computed as `total_rows // 10`, ensuring the number of DB round-trips scales sublinearly with dataset size. A 10,000-row job does ~10 bulk inserts rather than 10,000 individual writes.

---

## Middleware Stack

Requests pass through the following layers before reaching route handlers:

```
Incoming request
  │
  ├─ LoggingMiddleware
  │    ├─ Generates request_id (8-char UUID prefix)
  │    ├─ Binds request_id, method, path to structlog contextvars
  │    ├─ Logs request_started (info)
  │    └─ Logs request_finished with status_code and duration_ms (info)
  │
  └─ Route handler
       └─ verify_api_key dependency (on all routes except /health)
```

`LoggingMiddleware` uses `structlog.contextvars.bound_contextvars` to bind the `request_id` for the duration of the request. Any `logger.info/warning/error` call anywhere in the call chain — route handlers, service functions, utility modules — automatically inherits the `request_id` without it being passed as a parameter.

---

## Structured Logging

All application logging uses `structlog` configured to emit JSON to stdout. HF Spaces captures stdout and makes it available in the Space logs panel.

**Setup:** `setup_logging()` is called once at lifespan startup, before any other initialization. It configures structlog with ISO timestamps, log level tagging, exception formatting, and JSON rendering.

**Log levels used:**

| Level | When |
|---|---|
| `debug` | Preprocessing stages, raw inputs — not emitted in production (log level INFO) |
| `info` | Inference completed, job state transitions, cache hits, scheduler fired |
| `warning` | Gemini failed/falling back to Groq, low confidence result, invalid input, wrong API key |
| `error` | Both LLMs failed, DB write failed, inference threw exception, unhandled errors |
| `critical` | Model load failure at startup, missing required env vars |

**Example log line (inference completed):**
```json
{
  "event": "inference_completed",
  "model": "RoBERTa Transformer",
  "label": "Positive",
  "confidence": 0.9341,
  "duration_ms": 87.4,
  "request_id": "a3f9c1b2",
  "path": "/predict",
  "method": "POST",
  "timestamp": "2026-06-25T10:41:03Z",
  "level": "info"
}
```

**Background task logging:** Background tasks run outside the request's `contextvars` context. The `request_id` is extracted from contextvars inside the route handler before the response is sent, then passed as a parameter to the background task function. This allows the DB write log to carry the same `request_id` as the inference log even though it runs after the request completes.

---

## Authentication

All routes except `/health` require an `X-Api-Key` header. Verification is implemented as a FastAPI dependency injected at the router level:

```python
async def verify_api_key(x_api_key: str = Header(default=None)):
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Missing API key")
    if not secrets.compare_digest(x_api_key, settings.PROTECT_API_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
```

`secrets.compare_digest` is used instead of direct string comparison to prevent timing attacks. A wrong or missing key returns 401. Failed auth attempts are logged at `warning` level.

---

## Concurrency Model

The backend runs as a single Uvicorn worker. FastAPI's `BackgroundTasks` is used for batch jobs — each job runs in a background thread within the same process.

This means:

- Batch jobs do not block the HTTP event loop
- Multiple concurrent batch jobs would share the same process and GIL
- Model inference is CPU-bound; no GPU parallelism is available (HF Spaces CPU tier)
- `torch.set_num_threads(1)` is set explicitly to prevent PyTorch from spawning excessive threads during single-sample inference

The architecture is not designed for high concurrency of batch jobs. It is designed for sequential batch processing with real-time single inference available throughout.

---

## Model Runtime Architecture

Three models run in the same process, each with a different runtime backend:

| Model | Runtime | Loading Mechanism | Inference Format |
|---|---|---|---|
| Logistic Regression | scikit-learn | `joblib.load` | sparse TF-IDF matrix |
| Bi-LSTM | TensorFlow/Keras | `tf.keras.models.load_model` | padded integer sequences |
| RoBERTa | ONNX Runtime | `ort.InferenceSession` | tokenized numpy arrays |

RoBERTa is stored and served as a quantized ONNX model (`model_quantized.onnx`, INT8 dynamic quantization). This avoids the PyTorch dependency for inference while reducing model size and improving CPU throughput compared to the original weights.

---

## Model Registry and Loading Strategy

`model_registry.py` defines the registry of available models: their HuggingFace Hub repo IDs and loader functions. `model_loader.py` implements lazy loading with an in-process cache (`loaded_models` dict).

```
At startup (lifespan):
  setup_logging()  → structlog configured first, before anything else
  preload_models() → loads all three models into loaded_models
  warmup()         → runs a dummy inference through each pipeline

At request time:
  get_model(name)  → returns from loaded_models (no disk I/O)
```

Models are downloaded from HuggingFace Hub at container startup via `snapshot_download`. The downloaded paths are resolved once and used for all subsequent loads. After the initial cold start, all inference operates from in-memory loaded objects.

The warmup pass ensures TensorFlow and ONNX runtimes have initialized their internal graphs before serving real requests, preventing artificially high latency on the first inference.

---

## Data Storage Schema

| Table | Purpose |
|---|---|
| `logs` | One row per live inference request — text, prediction, confidence, probabilities, latency, status |
| `batch_jobs` | One row per batch upload — status, timing breakdown, throughput, progress |
| `batch_results` | One row per prediction within a batch job |
| `batch_summaries` | LLM-generated reports, cached by `(job_id, summary_type)` |
| `overview_insights` | Scheduled LLM-generated system insights, one row per generation cycle |

`batch_summaries` has a unique constraint on `(job_id, summary_type)`. Requesting a summary for a job that already has one returns the cached version without an LLM call.

---

## Design Decisions

**Single-process model hosting.** All three models are loaded into the same FastAPI process. This eliminates inter-process serialization overhead and simplifies deployment at the cost of higher memory usage and no model-level isolation.

**Synchronous background tasks over a task queue.** FastAPI `BackgroundTasks` is sufficient for the single-job-at-a-time batch workload. Introducing Celery or a similar queue would add operational complexity without clear benefit at this scale.

**Preprocessing is model-specific, not shared.** Each model has its own preprocessing path because their input requirements differ meaningfully — Logistic Regression requires clean ASCII tokens, Bi-LSTM requires lowercased text, RoBERTa requires minimal preprocessing to preserve subword tokenization. A shared preprocessing step would either under-process for some models or over-process for others.

**LLM calls are synchronous within the request.** For live inference, the LLM insight call happens inline and adds latency. This was accepted as a tradeoff for simplicity; the insight is part of the primary response payload rather than a separate async fetch.

**Exception handling layering.** `HTTPException` is re-raised directly so FastAPI handles it as intended. All other exceptions are caught, logged at `error` level with `exc_info=True` for full traceback capture, and converted to 500 responses. This prevents `HTTPException` from being accidentally swallowed by broad `except Exception` blocks.