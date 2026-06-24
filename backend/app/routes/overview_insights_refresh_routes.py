from fastapi import APIRouter, Depends
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.services.insights_service.overview_insights import generate_and_save_insights

from app.core.security import verify_api_key
from app.core.dependencies import get_db

router = APIRouter()

@router.post("/overview_insights/refresh")
def refresh_insights(db: Session = Depends(get_db), _:bool=Depends(verify_api_key)):
    try:
        generate_and_save_insights()
        return {"message": "Insights refreshed successfully."}
    except Exception as e:
        print(f"Refresh failed: {type(e).__name__}: {e}")
        return {"message": f"Failed to refresh: {e}"}