from models.log_models import Log

def get_logs(db):
    logs = db.query(
        Log.text,
        Log.prediction,
        Log.model,
        Log.confidence,
        Log.negative,
        Log.neutral,
        Log.positive,
        Log.latency,
        Log.status,
        Log.timestamp
    ).order_by(Log.timestamp.desc()).limit(50).all()

    sentiment_map = {
        "0": "Negative",
        "1": "Neutral",
        "2": "Positive"
    }

    analytics = [
        {
            "text":row[0],
            "prediction":sentiment_map.get(str(row[1]), "unknown"),
            "model":row[2],
            "confidence":row[3],
            "negative":row[4],
            "neutral":row[5],
            "positive":row[6],
            "latency":row[7],
            "status":row[8],
            "timestamp":row[9]
        }
        for row in logs
    ]

    return analytics