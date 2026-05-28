from sqlalchemy import func, case
from models.log_models import Log
from app.schemas.request_schema import InputData
from datetime import datetime, timedelta, UTC

def get_inference_metrics(db):
    one_minute_ago = datetime.now(UTC) - timedelta(minutes=1)

    metrics = db.query(
        func.count(Log.id).label("total_predictions"),
        func.avg(Log.latency).label("average_latency"),
        func.avg(Log.negative).label("negative_avg"),
        func.avg(Log.neutral).label("neutral_avg"),
        func.avg(Log.positive).label("positive_avg"),
        (func.count(case((Log.status == "success", 1))) * 100.0 / func.count(Log.id)).label("success_rate"),
        (func.count(case((Log.status == "error", 1))) * 100.0 / func.count(Log.id)).label("failure_rate")
        ).first()

    rpm = db.query(Log).filter(
        Log.timestamp >= one_minute_ago
    ).count()

    return {
        "total_predictions": metrics.total_predictions,
        "average_latency": round(metrics.average_latency or 0, 3)*1000,
        "rpm": rpm,
        "throughput": int(1/metrics.average_latency) if metrics.average_latency>0 else 0,
        "success_rate": metrics.success_rate,
        "failure-rate": metrics.failure_rate
    }

def get_inference_row_metrics(db):
    metrics = db.query(
        Log.prediction.label("sentiment"),
        func.greatest(Log.negative, Log.neutral, Log.positive).label("confidence_score"),
        Log.model.label("model"),
        Log.latency.label("latency")
    ).order_by(Log.timestamp.desc()).first()
    
    if not metrics:
        return {
            "sentiment": "No data available",
            "confidence": "No data available",
            "certainty": "No data available",
            "severity": "No data available",
            "model": "No data available",
            "runtime": "No data available"
        }

    map_sentiment = {'0': "Negative", "1": "Neutral", "2": "Positive"}
    inference_sentiment = map_sentiment.get(metrics.sentiment, "No data available.")

    conf_score = metrics.confidence_score
    if conf_score<40:
        severity = "Low"
        certainty = "HIGH CERTAINTY"
    elif conf_score<70:
        severity = "Medium"
        certainty = "MODERATE CERTAINTY"
    else:
        severity = "High"
        certainty = "LOW CONFIDENCE"

    return {
        "sentiment": inference_sentiment,
        "confidence": metrics.confidence_score,
        "severity": severity,
        "certainty": certainty,
        "model": metrics.model,
        "runtime": f"{round(metrics.latency, 2)*1000}ms"
    }