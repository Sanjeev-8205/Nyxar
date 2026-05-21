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
        "best_model": "RoBERTa Transformer",
        "success_rate": metrics.success_rate,
        "failure-rate": metrics.failure_rate
    }