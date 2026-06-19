# Observability

## Telemetry Architecture

Observability is split across two layers: a relational telemetry layer (PostgreSQL, queried at request time) and a metrics scrape layer (Prometheus, scraped by Grafana).

```
Inference requests
       │
       ├──► PostgreSQL logs table     ← structured, queryable, drives dashboard
       └──► Prometheus counters/      ← time-series, drives Grafana
            histograms/gauges

Batch jobs
       │
       ├──► batch_jobs table          ← job metadata, timing, throughput
       ├──► batch_results table       ← per-row predictions
       └──► Prometheus batch metrics

LLM calls
       ├──► batch_summaries table     ← cached reports, token counts
       └──► Prometheus LLM metrics
```

The `/dashboard` endpoint aggregates from PostgreSQL across six metric service modules and returns everything in a single response. The Streamlit frontend calls this once per page load (with a 15-second TTL cache) rather than making separate calls per chart.

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

**PostgreSQL as the telemetry store.** All inference logs are structured relational data with known schemas. The analytics queries (drift windows, latency percentiles, distribution aggregates) are well-suited to SQL. A time-series database would be appropriate at higher volume but adds operational overhead that isn't justified at this scale.

**P95 latency via SQL percentile functions.** `func.percentile_cont(0.95).within_group(Log.latency)` computes the p95 directly in the database rather than pulling all rows into Python. This keeps the query efficient even as the logs table grows.

**Prometheus for Grafana integration.** Prometheus metrics are collected in-process using the `prometheus_client` library. The `/prometheus_metrics` endpoint exposes them in the standard text format. This allows any Prometheus-compatible scraper (Grafana Cloud, self-hosted Prometheus) to collect metrics without changes to the application.

**Auth on the metrics endpoint.** The `/prometheus_metrics` endpoint is protected with HTTP Basic Auth. Without this, the endpoint would expose inference volumes, model usage patterns, and system health data publicly.
