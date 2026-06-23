from prometheus_client import Counter, Histogram, Gauge

# Inference Metrics

LIVE_INFERENCE_REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests"
)

LIVE_INFERENCE_PREDICTION_COUNT = Counter(
    "predictions_total",
    "Total successful predictions",
    ["model"]
)

LIVE_INFERENCE_ERROR_COUNT = Counter(
    "prediction_errors_total",
    "Total prediction failures"
)

REQUEST_LATENCY_SINGLE_INFERENCE = Histogram(
    "request_latency_milliseconds(Single Inference)",
    "Request latency in milliseconds",
    ["model"]
)

LIVE_INFERENCE_PREDICTION_LATENCY = Histogram(
    "prediction_latency_milliseconds",
    "Prediction latency in milliseconds",
    ["model"]
)

MODEL_PREDICTION_CONFIDENCE = Histogram(
    "prediction_confidence",
    "Prediction Confidence",
    ["model"]
)

MODEL_PREDICTION_CONFIDENCE_GAUGE = Gauge(
    "prediction_confidence_accurate",
    "Prediction_Confidence_Accurate",
    ["model"]
)

LATENCY_BREAKDOWN = Histogram(
    "nyxar_components_latency_breakdown",
    "Latency by component",
    ["latency_type"]
)

LLM_LATENCY_BREAKDOWN = Histogram(
    "llm_latency_breakdown",
    "Latency Breakdown by llm",
    ["provider"]
)

LLM_STATUS_COUNT = Counter(
    "status_count",
    "llm status by model",
    ["provider", "status"]
)

LLM_FALLBACK_COUNT = Counter(
    "fallback_count",
    "LLM fallback count",
)

LLM_INPUT_TOKENS = Histogram(
    "llm_input_tokens",
    "Input tokens by provider",
    ["provider"]
)

LLM_OUTPUT_TOKENS = Histogram(
    "llm_output_tokens",
    "Output tokens by provider",
    ["provider"]
)

LLM_REQUEST_COUNT = Counter(
    "llm_count",
    "LLM Count",
    ["provider"]
)

LLM_INSIGHT_GENERATION_LATENCY = Histogram(
    "llm_insight_generation_latency",
    "End-to-end insight generation latency"
)

## Model Metrics

ACTIVE_MODELS = Gauge(
    "active_models_loaded",
    "Number of loaded models"
)

# Batch Metrics
TOTAL_BATCH_JOBS = Counter(
    "total_batch_jobs",
    "Total_Batch_Jobs",
    ["model", "status"]
)

TOTAL_PROCESSED_ROWS = Histogram(
    "total_rows_processed_per_batch_job",
    "Total Rows Processed",
    ["model"]
)

JOB_DURATION = Histogram(
    "Total_job_time_in_seconds",
    "Job Duration",
    ["model"]
)

JOB_THROUGHPUT = Histogram(
    "rows_processed_per_second",
    "Job Throughput",
    ["model"]
)

JOB_THROUGHPUT_GAUGE = Gauge(
    "rows_processed_per_second_gauge",
    "Job Throughput Gauge",
    ["model"]
)

JOB_ML_PROCESSING_TIME = Histogram(
    "ml_processing_time_per_job",
    "ML Processing Time Distribution",
    ["model"]
)

JOB_ML_PROCESSING_TIME_GAUGE = Gauge(
    "ml_processing_time_per_job_gauge",
    "ML Processing Time Distribution Gauge",
    ["model"]
)

#LLM - AI Intelligence Page
TOTAL_SUMMARY_REQUESTS = Counter(
    "llm_summary_requests",
    "Total LLM Requests",
    ["summary_type", "status"]
)

TOTAL_FALLBACKS = Counter(
    "llm_model_fallback",
    "Model Fallback count",
    ["summary_type", "failed_model", "fallback_model"]
)

LLM_LATENCY = Histogram(
    "llm_latency_seconds",
    "LLM Latency(Seconds)",
    ["summary_type", "model_used"] 
)

LLM_REQUESTS_BY_MODEL = Counter(
    "llm_requests_by_model",
    "Requests by LLM",
    ["model_used"]
)

REQUEST_LATENCY = Histogram(
    "full_request_latency_seconds",
    "Full Request Latency(Seconds)",
    ["model_used"]
)