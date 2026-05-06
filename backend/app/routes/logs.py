from fastapi import APIRouter
from app.core.database import SessionLocal
from models.log_models import Log
import pandas as pd

router = APIRouter()

@router.get("/logs")
def get_logs():
    db = SessionLocal()

    try:
        logs = db.query(
            Log.text,
            Log.prediction,
            Log.model,
            Log.negative,
            Log.neutral,
            Log.positive,
            Log.latency,
            Log.timestamp
        ).order_by(Log.timestamp.desc()).limit(10).all()
    
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
                "negative":row[3],
                "neutral":row[4],
                "positive":row[5],
                "latency":row[6],
                "timestamp":row[7]
            }
            for row in logs
        ]

        return analytics
    
    finally:
        db.close()