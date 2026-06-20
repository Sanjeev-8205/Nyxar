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

The original RoBERTa model ran under PyTorch. On CPU, a 500-row batch took approximately 70 seconds. After converting to ONNX and applying INT8 dynamic quantization, the same workload runs in approximately 25 seconds.

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

Fallback events are tracked in Prometheus (`llm_model_fallback` counter with `failed_model` and `fallback_model` labels) so the frequency and pattern of failures is observable in Grafana.

LLM reports (`batch_summaries`) are cached in PostgreSQL with a unique constraint on `(job_id, summary_type)`. Requesting the same report twice returns the cached version, avoiding redundant LLM calls and ensuring consistent results for the same dataset.
