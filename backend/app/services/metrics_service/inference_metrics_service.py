from sqlalchemy import func
from models.log_models import Log
from app.schemas.request_schema import InputData
from datetime import datetime, timedelta

def get_inference_metrics(db):
    one_minute_ago = datetime.now() - timedelta(minutes=1)

    metrics = db.query(
        func.count(Log.id).label("total_predictions"),
        func.avg(Log.latency).label("average_latency"),
        func.avg(Log.negative).label("negative_avg"),
        func.avg(Log.neutral).label("neutral_avg"),
        func.avg(Log.positive).label("positive_avg")
        )

    rpm = db.query(Log).filter(
        Log.timestamp >= one_minute_ago
    ).count()

    return {
        "total_predictions": metrics.total_predictions,
        "average_latency": round(metrics.average_latency or 0, 3),
        "negative_avg": round(metrics.negative_avg or 0, 3),
        "neutral_avg": round(metrics.neutral_avg or 0, 3),
        "positive_avg": round(metrics.positive_avg or 0, 3),
        "currently_selected_model": InputData.model,
        "rpm": rpm
    }