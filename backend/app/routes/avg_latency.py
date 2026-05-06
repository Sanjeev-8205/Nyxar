from fastapi import APIRouter
from sqlalchemy import func
from app.core.database import SessionLocal
from models.log_models import Log

router=APIRouter()

@router.get("/avg_latency")
def get_avg_latency():
    db = SessionLocal()

    try:
        average_latency=db.query(
            Log.model,
            func.avg(Log.latency).label("avg_latency")
        ).group_by(Log.model).all()

        analytics = []

        for row in average_latency:
            analytics.append({
                "model": row[0],
                "avg_latency": float(row[1])
            })

        return analytics
    
    finally:
        db.close()