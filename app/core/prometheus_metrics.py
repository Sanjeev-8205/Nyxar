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

REQUEST_LATENCY = Histogram(
    "request_latency_milliseconds",
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

JOB_ML_PROCESSING_TIME = Histogram(
    "ml_processing_time_per_job",
    "ML Processing Time Distribution",
    ["model"]
)