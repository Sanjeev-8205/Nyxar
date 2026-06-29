from models.log_models import Log
from models.batch_job_model import BatchJob
from datetime import datetime, UTC
from sqlalchemy import func, case, text

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

    from sqlalchemy import text


def get_predictions_over_time(db):
    # Daily predictions
    daily_results = db.execute(
        text("""
            SELECT
                DATE(timestamp) AS day,
                COUNT(id) AS count
            FROM logs
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        """)
    ).mappings().all()

    # Hourly predictions
    hourly_results = db.execute(
        text("""
            SELECT
                date_trunc('hour', timestamp) AS hour,
                COUNT(id) AS count
            FROM logs
            GROUP BY date_trunc('hour', timestamp)
            ORDER BY date_trunc('hour', timestamp)
        """)
    ).mappings().all()

    prediction_per_day = [
        {
            "day": row["day"],
            "count": row["count"]
        }
        for row in daily_results
    ]

    prediction_per_hour_each_day = [
        {
            "hour": row["hour"],
            "count": row["count"]
        }
        for row in hourly_results
    ]

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
    query = text("""
        SELECT
            CASE
                WHEN GREATEST(negative, neutral, positive) < 0.2 THEN '0-20'
                WHEN GREATEST(negative, neutral, positive) < 0.4 THEN '20-40'
                WHEN GREATEST(negative, neutral, positive) < 0.6 THEN '40-60'
                WHEN GREATEST(negative, neutral, positive) < 0.8 THEN '60-80'
                ELSE '80-100'
            END AS confidence_bucket,
            COUNT(*) AS count
        FROM logs
        GROUP BY confidence_bucket
        ORDER BY confidence_bucket;
    """)

    rows = db.execute(query).mappings().all()

    return [
        {
            "Confidence": row["confidence_bucket"],
            "Count": row["count"],
        }
        for row in rows
    ]

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
            "id": recent_batch_job.id if recent_batch_job else "No batch jobs yet",
            "status": recent_batch_job.status if recent_batch_job else "No batch jobs yet",
            "rows_processed": recent_batch_job.processed_rows if recent_batch_job else "No batch jobs yet",
            "model_used": recent_batch_job.model_name if recent_batch_job else "No batch jobs yet"
        }
    }

    return results

def get_throughput_per_hour(db):
    query = text("""
        SELECT
            date_trunc('hour', timestamp) AS hour,
            CASE
                WHEN AVG(latency) > 0
                THEN 1.0 / AVG(latency)
                ELSE 0
            END AS throughput
        FROM logs
        GROUP BY date_trunc('hour', timestamp)
        ORDER BY date_trunc('hour', timestamp);
    """)

    rows = db.execute(query).mappings().all()

    return [
        {
            "hour": row["hour"],
            "throughput": float(row["throughput"])
        }
        for row in rows
    ]