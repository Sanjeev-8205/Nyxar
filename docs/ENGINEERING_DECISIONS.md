# Engineering Decisions

## Why FastAPI

FastAPI was chosen over Flask or Django for three specific reasons: native async support, automatic OpenAPI schema generation, and `BackgroundTasks` for dispatching batch jobs without a separate worker process.

The `BackgroundTasks` pattern handles the batch processing use case cleanly — the upload endpoint returns immediately with a `job_id`, and the processing runs in the background without blocking the event loop. This avoids the operational overhead of Celery, Redis, or a separate worker service for a workload that processes one job at a time.

Pydantic schema validation on request bodies (`InputData`) catches malformed requests at the boundary before they reach ML code.

---

## Why Streamlit

The frontend requirement was a data-intensive dashboard with charts, file uploads, polling loops, and session state — not a user-facing product with custom interaction patterns. Streamlit covers this without requiring a separate JavaScript build pipeline or frontend deployment.

The tradeoff is layout control. Streamlit's component model is rigid, so UI customization beyond what the built-in components support requires injecting raw HTML and CSS via `st.markdown(..., unsafe_allow_html=True)`. This is used extensively in `components.py` for cards, status indicators, trace visualizations, and metric layouts.

The UI and backend are independently deployed. The frontend is entirely stateless with respect to the backend — all state is either in Streamlit session state or fetched from the API.

---

## Why PostgreSQL

All telemetry data — inference logs, batch jobs, batch results, LLM summaries, overview insights — is structured and relational. The analytics workload is read-heavy with known query patterns: aggregations, percentile calculations, time-bucketed counts, and joins across a handful of tables.

SQL handles all of this without additional infrastructure. Specific cases where the database does meaningful work:

- `func.percentile_cont(0.95).within_group(Log.latency)` — p95 latency computed in-database
- `func.date_trunc("hour", Log.timestamp)` — hourly aggregations for trend charts
- Bulk INSERT via SQLAlchemy `insert()` for batch result writes

Neon was chosen as the hosted provider for its serverless connection model and proximity to the HF Spaces deployment region (us-east-1). The `pool_pre_ping` and `pool_recycle` settings in the SQLAlchemy engine configuration handle Neon's connection behavior correctly.

---

## Why ONNX Runtime for RoBERTa

The original RoBERTa model ran under PyTorch. On CPU, a 500-row batch took approximately 70 seconds. After converting to ONNX and applying INT8 dynamic quantization, the same workload now runs in 25–35 seconds on average.

The conversion path:
1. Export to ONNX via `optimum.onnxruntime.ORTModelForSequenceClassification`
2. Apply dynamic quantization via `onnxruntime.quantization.quantize_dynamic` with `QInt8` weight type

ONNX Runtime's CPU execution provider is more efficient than PyTorch's CPU path for inference-only workloads because it applies graph optimizations (operator fusion, constant folding) that PyTorch does not apply by default.

The quantized model trades a small amount of precision for a meaningful reduction in inference time and memory footprint. Given the model's 77.6% accuracy on the test set, this tradeoff is acceptable — the accuracy loss from INT8 quantization is negligible relative to the inherent uncertainty in the task.

RoBERTa inference is batched in chunks of 64 rows. This is the primary source of efficiency for large batch jobs — tokenizing and running the ONNX session once per 64 samples rather than once per sample.

---

## Why Hugging Face Hub for Model Storage

Bundling model files in the Docker image would make every application code change trigger a full model re-download during the Docker build, significantly slowing CI. More importantly, it would couple model versioning to application versioning.

Storing models on separate HF Hub repos means:
- Model artifacts can be updated independently of application code
- The Docker image stays small (dependencies only, no weights)
- `snapshot_download` handles caching and integrity verification

The tradeoff is cold start time. Container startup requires downloading model files from Hub before serving requests. This is acceptable for the HF Spaces deployment model, where containers are long-lived and cold starts are infrequent relative to serving time.

---

## Why Prometheus

The existing observability stack (PostgreSQL + dashboard queries) covers analytical metrics well but cannot serve time-series data to external systems or generate alerts.

Prometheus integration adds:
- Grafana Cloud compatibility via the standard scrape protocol
- Counters and histograms that accumulate across requests without database queries
- Alert rule support in Grafana based on metric thresholds

The `prometheus_client` library instruments the application in-process. No sidecar or exporter is needed. The `/prometheus_metrics` endpoint exposes the collected data in the standard text format.

HTTP Basic Auth on the endpoint prevents the inference volume, model usage, and system health data from being publicly readable.

---

## Why structlog for Structured Logging

Plain `print()` statements and Python's standard `logging` module produce unstructured text. When multiple concurrent requests are in flight, their log lines are interleaved with no way to group them by request.

`structlog` solves this in two ways:

**JSON output** — every log line is a machine-readable JSON object with consistent fields (`event`, `level`, `timestamp`, plus any bound context). This makes logs greppable and parseable in HF Spaces logs without regex.

**`contextvars` integration** — `LoggingMiddleware` binds a `request_id` to the current async task's context at the start of every request. Every `logger.info/warning/error` call anywhere in the call chain — including in `ml_service.py`, `logging_service.py`, or any other module — automatically includes the `request_id` without it being passed as a parameter. This makes it possible to filter all log lines for a single request out of a busy log stream.

For background tasks (DB writes, batch processing), `contextvars` is not inherited because the task runs after the request context is destroyed. The `request_id` is extracted from `contextvars` inside the route handler before the response is sent and passed explicitly as a function parameter, maintaining traceability across the request/background-task boundary.

`structlog` was chosen over `python-json-logger` because it has a cleaner API for binding contextual fields, native `contextvars` support, and composable processor pipelines.

---

## Why API Key Auth (and Not JWT)

JWT authentication requires issuing tokens, managing expiry, and validating signatures on every request. For an API with a single trusted client (the Streamlit frontend), this is unnecessary complexity.

A pre-shared API key stored in HF Spaces Secrets and Streamlit Cloud Secrets achieves the same goal: only the authorized client can hit the API. The implementation is a single FastAPI dependency injected at the router level.

`secrets.compare_digest` is used instead of `==` for string comparison. Direct string comparison in Python short-circuits as soon as it finds a differing character, which leaks timing information that can be exploited to brute-force the key one character at a time. `compare_digest` takes constant time regardless of where the strings differ, eliminating this attack vector.

Missing key and wrong key both return 401. Failed attempts are logged at `warning` level so brute-force attempts are visible in logs.

---

## Why Tag-Based Deploys

Auto-deploying on every push to `main` means a one-line comment fix and a major feature ship through the same pipeline with the same weight. There is no concept of a deliberate release decision.

Tag-based deploys (`v*` tags) introduce an explicit "I am ready to ship this" signal. Regular pushes to `main` run the test suite only. A deploy only happens when a tag is pushed or the workflow is triggered manually.

This also makes the HF Spaces deployment history meaningful — each commit on the Space corresponds to a tagged release, not every incremental change.

`workflow_dispatch` is kept alongside the tag trigger so a forced redeploy (e.g. after rotating a secret on HF Spaces) is possible without creating a dummy tag.

The commit message on HF Spaces is derived from `git log -1 --pretty=%s ${{ github.sha }}` rather than `github.event.head_commit.message`. The `head_commit` field is not populated for tag-triggered workflows, which would produce empty commit messages. The `git log` approach works correctly for all three trigger types: tag push, branch push, and manual dispatch.

---

## Why Three Models

Three models were included to serve different tradeoffs explicitly, rather than picking one.

| Model | Tradeoff |
|---|---|
| Logistic Regression | Minimal latency, minimal memory, lowest accuracy |
| Bi-LSTM | Moderate latency, captures sequential context |
| RoBERTa (ONNX, INT8) | Highest accuracy, highest resource cost |

Having all three available in the same system makes the accuracy/latency tradeoff visible and measurable. The `/dashboard` endpoint exposes average latency per model alongside the model performance metrics from `metrics/*.json`, making comparisons concrete rather than theoretical.

The evaluation script (`evaluate.py`) runs all three models against the same test set and writes results to `metrics/*.json`. These files are committed to the repository and served directly by the dashboard.

---

## Why Gemini + Groq Fallback

Three separate LLM use cases exist in the system: live inference insights, batch job insights, and LLM-generated reports. All three use the same pattern: Gemini as primary, Groq as fallback.

**Gemini (`gemini-3.1-flash-lite`)** is the primary because it supports structured JSON output via `response_mime_type="application/json"`, which eliminates the need to parse and validate freeform text. It also supports a `thoughts_token_count` field in usage metadata, which is tracked in the database.

**Groq (`llama-3.1-8b-instant` / `meta-llama/llama-4-scout-17b-16e-instruct`)** is the fallback because it has different rate limits and availability characteristics. When Gemini fails (rate limits, API errors), Groq handles the request. The fallback is transparent to the user.

Fallback events are tracked in two places: Prometheus (`llm_model_fallback` counter with `failed_model` and `fallback_model` labels) for Grafana visibility, and structlog (`warning` level with `provider`, `error`, and fallback provider fields) for per-request traceability in HF Spaces logs.

LLM reports (`batch_summaries`) are cached in PostgreSQL with a unique constraint on `(job_id, summary_type)`. Requesting the same report twice returns the cached version, avoiding redundant LLM calls and ensuring consistent results for the same dataset.

---

## V2 Planned Decisions

**Grafana Loki for structured log storage.** structlog currently emits JSON to stdout, readable in HF Spaces logs panel but not queryable or alertable. Loki is the natural v2 addition — it is already available in Grafana Cloud alongside the existing Prometheus setup, requires no new account or infrastructure, and is purpose-built for JSON structured logs. Every field structlog emits (`request_id`, `model`, `confidence`, `duration_ms`) becomes a queryable label in LogQL. The key capability this unlocks is log-metric correlation in Grafana — clicking a latency spike on a Prometheus panel can show the exact structlog lines from that time window. Integration is via the Loki HTTP push endpoint called from a structlog processor, avoiding the need for a Promtail sidecar on HF Spaces.

**Alembic for schema migrations.** `Base.metadata.create_all()` handles initial table creation but cannot alter existing tables. As the schema evolves — new columns on `batch_jobs`, additional telemetry fields on `logs` — manual DDL on Neon becomes a reliability risk. Alembic with autogenerate against SQLAlchemy models produces versioned migration scripts that run at deploy time and are fully reversible.

**Per-model latency SLOs.** Prometheus already collects per-model p95 histograms. SLO monitoring is adding Grafana alert rules on top of existing data — no new instrumentation required. Alert thresholds will be model-specific (RoBERTa tolerates higher latency than Logistic Regression) and will fire to a notification channel when sustained p95 exceeds the defined budget.

**Confidence calibration.** The current confidence scores are raw softmax outputs, which are not guaranteed to be calibrated — a 90% confidence score does not necessarily mean the model is correct 90% of the time. A reliability diagram (plotting mean predicted confidence vs actual accuracy in bins) run against the held-out test set will quantify whether scores are trustworthy as probability estimates. If miscalibrated, temperature scaling can be applied post-hoc without retraining.

**Drift alerting.** Drift detection currently runs on every `/dashboard` call and is displayed as a passive chart. v2 will add Grafana alert rules on the Prometheus confidence gauge and sentiment metrics, firing when rolling shift values exceed configured thresholds. This converts passive drift visibility into an active signal — as an internal tool operator you should not have to check a dashboard to know the model is drifting.