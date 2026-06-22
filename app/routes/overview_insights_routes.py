from fastapi import APIRouter, Depends
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from models.overview_insights_model import OverviewInsights
from app.core.security import verify_api_key

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()

        yield db

    finally:
        db.close()

@router.get("/overview_insights")
def get_insights(
    db: Session=Depends(get_db), _:bool=Depends(verify_api_key)
):
    results = db.query(
        OverviewInsights.created_at,
        OverviewInsights.ai_insights.label("insights")
    ).order_by(OverviewInsights.created_at.desc()).first()

    if results:
        return {
            "ai_insights": results.insights
        }
    
    else:
        return {
        "ai_insights": {
            "inference_insights": None,
            "recent_activity": None,
            "anomaly_detection": None,
            "health_metrics": None
        }
    }