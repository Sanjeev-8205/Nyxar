from prometheus_client import Counter, Histogram, Gauge

# API Metrics

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests"
)

PREDICTION_COUNT = Counter(
    "predictions_total",
    "Total successful predictions"
)

ERROR_COUNT = Counter(
    "prediction_errors_total",
    "Total prediction failures"
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds"
)

# Model Metrics

ACTIVE_MODELS = Gauge(
    "active_models_loaded",
    "Number of loaded models"
)