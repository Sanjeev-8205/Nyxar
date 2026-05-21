from fastapi import APIRouter, Depends
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from models.overview_insights_model import OverviewInsights

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()

        yield db

    finally:
        db.close()

@router.get("/overview_insights")
def get_insights(
    db: Session=Depends(get_db)
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
            "ai_insights": {}
        }