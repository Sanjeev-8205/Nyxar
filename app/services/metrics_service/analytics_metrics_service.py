from models.log_models import Log
from models.batch_job_model import BatchJob
from datetime import datetime, UTC
from sqlalchemy import func, case

def get_sentiment_distribution(db):
    sentiment_distribution = db.query(
        Log.prediction,
        func.count(Log.prediction)
    ).group_by(Log.prediction).all()

    pred_counts = {}
    for prediction, count in sentiment_distribution:
        pred_counts[prediction] = count

    total = sum(pred_counts.values())
    return {
        "Negative": pred_counts.get("0", 0),
        "Neutral": pred_counts.get("1", 0),
        "Positive": pred_counts.get("2", 0)
    }

def get_predictions_over_time(db):
    predictions_per_day = db.query(
        func.date_trunc("day", Log.timestamp).label("day"),
        func.count(Log.id).label("count")
    ).group_by(func.date_trunc("day", Log.timestamp)).order_by(
        func.date_trunc("day", Log.timestamp)
    ).all()

    predictions_per_hour_each_day = db.query(
        func.date_trunc("hour", Log.timestamp).label("hour"),
        func.count(Log.id).label("count")
    ).group_by(func.date_trunc("hour", Log.timestamp)).order_by(
        func.date_trunc("hour", Log.timestamp)
    ).all()

    prediction_per_day = []
    for row in predictions_per_day:
        prediction_per_day.append({
            "day": row[0],
            "count": row[1]
        })
    
    prediction_per_hour_each_day = []
    for row in predictions_per_hour_each_day:
        prediction_per_hour_each_day.append({
            "hour": row[0],
            "count": row[1]
        })

    prediction_per_day.sort(key = lambda x: x["day"], reverse=False)
    prediction_per_hour_each_day.sort(key = lambda x: x["hour"], reverse=False)

    return [prediction_per_day, prediction_per_hour_each_day]

def get_model_usage_distribution(db):
    model_usage = db.query(
        Log.model,
        func.count(Log.model).label("count")
    ).group_by(Log.model).all()

    mod_distb = []
    for row in model_usage:
        mod_distb.append({
            "model": row[0],
            "usage": row[1]
        })
    
    return mod_distb

def get_latency_trends(db):
    latency_per_hour = db.query(
        func.extract("hour", Log.timestamp).label("bucket"),
        func.avg(Log.latency).label("latency")
    ).group_by(func.extract("hour", Log.timestamp)).order_by(func.extract("hour", Log.timestamp)).all()

    latencies_trend = db.query(
        func.date_trunc("hour", Log.timestamp).label("hour"),
        func.avg(Log.latency).label("avg_latency"),
        func.max(Log.latency).label("max_latency"),
        func.count(Log.id).label("request_count")
    ).group_by("hour").order_by("hour").all()

    latencies_hour_of_day = []
    for row in latency_per_hour:
        latencies_hour_of_day.append({
            "hour": row[0],
            "latency": row[1]
        })

    latencies_over_time = []
    for row in latencies_trend:
        latencies_over_time.append({
            "time": row[0].isoformat() if row[0] else None,
            "avg_latency": float(row[1]) if row[1] is not None else 0,
            "max_latency": float(row[2]) if row[2] is not None else 0,
            "requests": int(row[3]) if row[3] is not None else 0
        })

    latencies_over_time.sort(key = lambda x: x["time"], reverse=False)

    return [latencies_hour_of_day, latencies_over_time] 

def get_confidence_distribution(db):
    max_conf = func.greatest(
        Log.negative, Log.neutral, Log.positive
    )

    bucket = case(
        (max_conf<0.2, "0-20"),
        (max_conf<0.4, "20-40"),
        (max_conf<0.6, "40-60"),
        (max_conf<0.8, "60-80"),
        else_="80-100"
    ).label("confidence_bucket")

    bucket_grouping = db.query(
        bucket,
        func.count(Log.id).label("count")
    ).group_by(bucket).all()

    results = []
    for bucket, count in bucket_grouping:
        results.append({
            "Confidence": bucket,
            "Count": count
        })

    return results

def get_recent_activity_feed(db):
    recent_activity = db.query(
        Log.prediction,
        Log.model.label("model"),
        Log.timestamp,
        Log.latency
    ).order_by(Log.timestamp.desc()).first()

    recent_batch_job = db.query(
        BatchJob.id.label("id"), BatchJob.status.label("status"),
        BatchJob.processed_rows.label("processed_rows"), BatchJob.model_name.label("model_name")
    ).order_by(BatchJob.created_at.desc()).first()

    if not recent_activity:
        return {
            "prediction": "No activity",
            "recent_activity": "No recent activity",
            "latency": 0
        }

    pred_map = {"0":"Negative", "1":"Neutral", "2":"Positive"}
    predicted_sentiment = pred_map.get(recent_activity[0], "unknown")

    seconds_since_last_activity = datetime.now(UTC) - recent_activity[2]
    
    total_seconds = seconds_since_last_activity.total_seconds()
    hours = int(total_seconds/3600)
    minutes = int((total_seconds%3600)/60)
    days = seconds_since_last_activity.days
    if total_seconds<60:
        res = f"{total_seconds} second{'s' if total_seconds!=1 else ''} ago"
    elif total_seconds<3600:
        res = f"{minutes} minute{'s' if minutes!=1 else ''} ago"
    elif days<1:
        res = f"{hours} hour{'s' if hours!=1 else ''} ago"
    else:
        res = f"{days} day{'s' if days!=1 else ''} ago"

    results = {
        "single_inference":{
            "prediction": f"{recent_activity.model} predicted {predicted_sentiment}",
            "recent_activity": res,
            "Latency": round(recent_activity[3],3)
        },
        "batch_jobs":{
            "id": recent_batch_job.id if recent_batch_job.id else "No batch jobs yet",
            "status": recent_batch_job.status if recent_batch_job.status else "No batch jobs yet",
            "rows_processed": recent_batch_job.processed_rows if recent_batch_job.processed_rows else "No batch jobs yet",
            "model_used": recent_batch_job.model_name if recent_batch_job.model_name else "No batch jobs yet"
        }
    }

    return results

def get_throughput_per_hour(db):
    throughput = db.query(
        func.date_trunc("hour", Log.timestamp).label("hour"),
        case((func.avg(Log.latency) > 0, 1 / func.avg(Log.latency)), else_=0).label("throughput")
    ).group_by(
        func.date_trunc("hour", Log.timestamp)
    ).order_by(
        func.date_trunc("hour", Log.timestamp)
    ).all()

    tph = []
    for row in throughput:
        tph.append({
            "hour": row[0],
            "throughput": row[1]
        })

    tph.sort(key = lambda x: x["hour"], reverse=False)

    return tph