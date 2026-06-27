# Observability

## Telemetry Architecture

Observability is split across three layers: a relational telemetry layer (PostgreSQL, queried at request time), a metrics scrape layer (Prometheus, scraped by Grafana), and a structured log layer (structlog, written to stdout and captured by HF Spaces).

```
Inference requests
       │
       ├──► PostgreSQL logs table      ← structured, queryable, drives dashboard
       ├──► Prometheus counters/       ← time-series, drives Grafana
       │    histograms/gauges
       └──► structlog JSON to stdout   ← per-request trace with request_id

Batch jobs
       │
       ├──► batch_jobs table           ← job metadata, timing, throughput
       ├──► batch_results table        ← per-row predictions
       └──► Prometheus batch metrics

LLM calls
       ├──► batch_summaries table      ← cached reports, token counts
       ├──► Prometheus LLM metrics
       └──► structlog warnings on fallback
```

The `/dashboard` endpoint aggregates from PostgreSQL across six metric service modules and returns everything in a single response. The Streamlit frontend calls this once per page load (with a 15-second TTL cache) rather than making separate calls per chart.

---

## Structured Logging

`structlog` is configured at lifespan startup to emit JSON to stdout. HF Spaces captures stdout and exposes it in the Space logs panel.

### Log Processors

```
structlog.stdlib.add_log_level       → adds "level" field
structlog.processors.TimeStamper     → adds "timestamp" (ISO format)
structlog.processors.format_exc_info → captures full traceback on exc_info=True
structlog.processors.JSONRenderer    → serializes to JSON string
```

### Request ID Tracing

`LoggingMiddleware` generates an 8-character `request_id` for every incoming request and binds it to the current async task via `structlog.contextvars.bound_contextvars`. All log calls in the request chain — across any module — automatically include the `request_id` without it being passed as a parameter.

For background tasks (DB writes after inference), the `request_id` is extracted from contextvars inside the route handler before the response is sent, then passed explicitly to the background task function. This preserves traceability across the request/background-task boundary.

### Log Events by Component

**Predict route:**

| Event | Level | Key Fields |
|---|---|---|
| `inference_request_received` | info | `model`, `input_length`, `has_text` |
| `inference_input_invalid` | warning | `model`, `input_length`, `reason` |
| `inference_preprocessing_started` | debug | `model`, `input_length` |
| `inference_preprocessing_completed` | debug | `model`, `original_length`, `processed_length`, `duration_ms` |
| `inference_model_started` | info | `model`, `processed_input_length` |
| `inference_completed` | info | `model`, `label`, `confidence`, `duration_ms` |
| `inference_low_confidence` | warning | `model`, `label`, `confidence` |
| `inference_failed` | error | `model`, `input_length`, `error`, `exc_info` |

**DB write (background task):**

| Event | Level | Key Fields |
|---|---|---|
| `inference_result_saved` | info | `model`, `prediction`, `db_write_duration_ms`, `request_id` |
| `inference_db_write_failed` | error | `model`, `prediction`, `error`, `exc_info`, `request_id` |

**LLM fallback:**

| Event | Level | Key Fields |
|---|---|---|
| `llm_insights_generated` | info | `provider` |
| `gemini_failed_falling_back_to_groq` | warning | `error` |
| `llm_both_providers_failed` | error | `gemini_error`, `groq_error`, `exc_info` |

**Middleware:**

| Event | Level | Key Fields |
|---|---|---|
| `request_started` | info | `request_id`, `method`, `path` |
| `request_finished` | info | `request_id`, `status_code`, `duration_ms` |

### Log Levels Reference

| Level | Meaning in Nyxar |
|---|---|
| `debug` | Preprocessing stages, raw inputs — filtered out at production log level |
| `info` | Normal successful operations |
| `warning` | Recovered failures — Gemini fallback, low confidence, wrong API key |
| `error` | Unrecovered failures — both LLMs failed, DB write failed, inference crashed |
| `critical` | Startup failures that make the app non-functional |

### Example Log Line

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

---

## Prometheus Metrics

Exposed at `GET /prometheus_metrics` with HTTP Basic Auth.

### Inference Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `api_requests_total` | Counter | — | Total requests to `/predict` |
| `predictions_total` | Counter | `model` | Successful predictions per model |
| `prediction_errors_total` | Counter | — | Failed predictions |
| `prediction_latency_milliseconds` | Histogram | `model` | ML inference latency |
| `request_latency_milliseconds(Single Inference)` | Histogram | `model` | Full request latency including logging |
| `prediction_confidence` | Histogram | `model` | Confidence score distribution |
| `prediction_confidence_accurate` | Gauge | `model` | Most recent confidence score |

### Model Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `active_models_loaded` | Gauge | — | Count of loaded models, set at startup |

### Batch Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `total_batch_jobs` | Counter | `model`, `status` | Completed and failed jobs |
| `total_rows_processed_per_batch_job` | Histogram | `model` | Row count distribution per job |
| `Total_job_time_in_seconds` | Histogram | `model` | End-to-end job duration |
| `rows_processed_per_second` | Histogram | `model` | Throughput distribution |
| `rows_processed_per_second_gauge` | Gauge | `model` | Most recent job throughput |
| `ml_processing_time_per_job` | Histogram | `model` | ML-only time within batch |
| `ml_processing_time_per_job_gauge` | Gauge | `model` | Most recent ML processing time |

### LLM Metrics

| Metric | Type | Labels | Description |
|---|---|---|---|
| `llm_summary_requests` | Counter | `summary_type`, `status` | Summary generation attempts |
| `llm_model_fallback` | Counter | `summary_type`, `failed_model`, `fallback_model` | Fallback events |
| `llm_latency_seconds` | Histogram | `summary_type`, `model_used` | LLM response time |
| `llm_requests_by_model` | Counter | `model_used` | Requests per LLM provider |
| `full_request_latency_seconds` | Histogram | `model_used` | Full summary request latency |

---

## Drift Monitoring

Drift detection runs over the full `logs` table on every `/dashboard` call. It operates on three signals:

**Input Length Drift** — tracks rolling mean of word count per inference request. Shifts indicate changes in the distribution of submitted text (shorter queries, longer documents, etc.).

**Sentiment Score Drift** — maps predictions to a numeric scale (Negative: -1, Neutral: 0, Positive: 1) and computes a rolling mean. A sustained shift in this value indicates the incoming data distribution is changing.

**Confidence Drift** — rolling mean of `max(negative, neutral, positive)` per prediction. A declining confidence trend may indicate the model is encountering out-of-distribution inputs.

All three use a rolling window of `min(20, n)` samples. Shift values compare the most recent `min(50, n//2)` samples against the preceding window of equal size.

```python
shift = mean(recent_window) - mean(previous_window)
```

Shift values are returned raw — not normalized — so consumers (UI, Prometheus) can apply their own thresholds.

---

## Platform Health Scoring

`platform_status_strip.py` computes a composite platform health score from six signals:

| Signal | Source | Scoring |
|---|---|---|
| Latency shift % | `get_latency_and_throughput_shifts` | +1 if >30%, +3 if >60% |
| Throughput shift % | `get_latency_and_throughput_shifts` | +1 if >25%, +3 if >50% |
| Confidence shift | `get_drift_indicators` | +1 if >0.10, +2 if >0.20 |
| Sentiment shift | `get_drift_indicators` | +1 if >0.15, +2 if >0.30 |
| Failure rate % | `get_failure_percent` | +2 if >1%, +4 if >5% |
| CPU usage % | `psutil.cpu_percent` | +1 if >75%, +3 if >90% |

**Score thresholds:**

| Score | Status | Color |
|---|---|---|
| 0–3 | PLATFORM STABLE | #10B981 (green) |
| 4–7 | PERFORMANCE WARNING | #F59E0B (amber) |
| 8+ | CRITICAL STATE | #EF4444 (red) |

The status string and color are returned directly to the frontend for display. No state is persisted — the score is recomputed on every request to `/platform_status`.

---

## LLM-Generated Operational Insights

Two separate insight generation flows exist:

**Overview Insights** — generated every 30 minutes via APScheduler. Collects inference metrics, recent activity, anomaly signals, and system health into a single telemetry payload, then calls Gemini (with Groq fallback) to generate four structured fields: `inference_insights`, `recent_activity`, `anomaly_detection`, `health_metrics`. Results are persisted to the `overview_insights` table. The UI reads the most recently saved row.

**Live Inference Insights** — generated inline on every `/predict` call. A short prompt containing the prediction, confidence, class probabilities, word count, and input text is sent to Gemini (Groq fallback). Returns a maximum 30-word natural language explanation of the prediction.

**Batch Job Insights** — generated once per batch job after completion. Analyzes throughput, timing breakdown, and model used. Persisted to `batch_jobs.ai_insights`.

---

## Design Decisions

**Three observability layers.** PostgreSQL covers queryable analytical history. Prometheus covers time-series metrics for Grafana. Structlog covers per-request event trails with full context. Each layer answers a different question: "what is the aggregate trend" (PostgreSQL/Prometheus), "what happened in this specific request" (structlog).

**PostgreSQL as the telemetry store.** All inference logs are structured relational data with known schemas. The analytics queries (drift windows, latency percentiles, distribution aggregates) are well-suited to SQL. A time-series database would be appropriate at higher volume but adds operational overhead that isn't justified at this scale.

**P95 latency via SQL percentile functions.** `func.percentile_cont(0.95).within_group(Log.latency)` computes the p95 directly in the database rather than pulling all rows into Python. This keeps the query efficient even as the logs table grows.

**Prometheus for Grafana integration.** Prometheus metrics are collected in-process using the `prometheus_client` library. The `/prometheus_metrics` endpoint exposes them in the standard text format. This allows any Prometheus-compatible scraper (Grafana Cloud, self-hosted Prometheus) to collect metrics without changes to the application.

**Auth on the metrics endpoint.** The `/prometheus_metrics` endpoint is protected with HTTP Basic Auth. Without this, the endpoint would expose inference volumes, model usage patterns, and system health data publicly.

**structlog over standard logging.** Python's standard logging module produces unstructured text. When multiple requests are in-flight, their log lines interleave with no grouping mechanism. `structlog` with `contextvars` solves this — every log line for a request shares a `request_id`, making per-request filtering possible in HF Spaces logs without any log aggregation infrastructure.

**Grafana Loki planned for v2.** structlog currently writes JSON to stdout, which HF Spaces captures in the logs panel. This is readable but not queryable or alertable. v2 will push logs directly to Grafana Cloud Loki via the Loki HTTP push endpoint, implemented as a structlog processor. Since Grafana Cloud is already in use for Prometheus, no new infrastructure is required. Loki will enable LogQL queries over structured fields (`request_id`, `model`, `level`), log-based alert rules (e.g. alert when `inference_db_write_failed` appears more than N times in 5 minutes), and correlated log-metric panels in the existing Grafana dashboard.