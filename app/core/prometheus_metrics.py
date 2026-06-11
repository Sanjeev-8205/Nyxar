from prometheus_client import Counter, Histogram, Gauge

# API Metrics

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
    "Request latency in milliseconds"
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

# Model Metrics

ACTIVE_MODELS = Gauge(
    "active_models_loaded",
    "Number of loaded models"
)