from sqlalchemy import func, case
from models.log_models import Log
from app.schemas.request_schema import InputData
from datetime import datetime, timedelta, UTC
from app.services.metrics_service.advanced_metrics_service import get_p95_latency

def get_inference_metrics(db):
    one_minute_ago = datetime.now(UTC) - timedelta(minutes=1)

    metrics = db.query(
        func.count(Log.id).label("total_predictions"),
        func.avg(Log.latency).label("average_latency"),
        func.avg(Log.negative).label("negative_avg"),
        func.avg(Log.neutral).label("neutral_avg"),
        func.avg(Log.positive).label("positive_avg"),
        func.coalesce((func.count(case((Log.status == "success", 1))) * 100.0/ func.nullif(func.count(Log.id), 0)),0.0,).label("success_rate"),
        func.coalesce((func.count(case((Log.status == "error", 1))) * 100.0/ func.nullif(func.count(Log.id), 0)),0.0,).label("failure_rate")
        ).first()

    rpm = db.query(Log).filter(
        Log.timestamp >= one_minute_ago
    ).count()

    return {
        "total_predictions": metrics.total_predictions,
        "average_latency": round(metrics.average_latency or 0, 3)*1000,
        "rpm": rpm,
        "throughput": (int(1 / metrics.average_latency) if metrics.average_latency and metrics.average_latency > 0 else 0),
        "success_rate": metrics.success_rate,
        "failure-rate": metrics.failure_rate
    }

def get_inference_row_metrics(db):
    metrics = db.query(
        Log.latency.label("latency"),
        Log.model.label("model")
    ).order_by(Log.timestamp.desc()).first()
    
    if not metrics:
        return {
            "latency_ms": "No data available",
            "latency_label": "No data available",
            "rpm": "No data available",
            "throughput_label": "No data available",
            "processing_time": "No data available",
            "model_name": "No data available",
            "model_family": "No data available",
            "model_runtime": "No data available"
        }

    # Latency
    latency_ms = (metrics.latency)*1000

    if latency_ms < 300:
        latency_label = "Excellent Response Time"

    elif latency_ms < 700:
        latency_label = "Good Response Time"

    elif latency_ms < 1200:
        latency_label = "Moderate Response Time"

    else:
        latency_label = "High Latency"

    #Throughput
    rpm = int(60/metrics.latency)

    if rpm > 200:
        throughput_label = "High Throughput"

    elif rpm > 100:
        throughput_label = "Stable Throughput"

    elif rpm > 50:
        throughput_label = "Moderate Throughput"

    else:
        throughput_label = "Low Throughput"

    model_metadata = {
        "Logistic Regression": {
            "family": "Linear Classifier",
            "runtime": "Scikit-Learn"
        },
        "Bi-LSTM": {
            "family": "Recurrent Neural Network",
            "runtime": "TensorFlow"
        },
        "RoBERTa Transformer": {
            "family": "Transformer",
            "runtime": "ONNX Runtime"
        }
    }

    return {
        "latency_ms": round(latency_ms, 2),
        "latency_label": latency_label,
        "rpm": rpm,
        "throughput_label": throughput_label,
        "processing_time": "Real-Time Processing",
        "model_name": metrics.model,
        "model_family": model_metadata[metrics.model]["family"],
        "model_runtime": model_metadata[metrics.model]["runtime"]
    }