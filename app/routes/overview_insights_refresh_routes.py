from fastapi import APIRouter, Depends
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.services.insights_service.overview_insights import generate_and_save_insights

router = APIRouter()

def get_db():
    try:
        db=SessionLocal()

        yield

    finally:
        db.close()

@router.post("/overview_insights/refresh")
def refresh_insights(db: Session = Depends(get_db)):
    try:
        generate_and_save_insights()
        return {"message": "Insights refreshed successfully."}
    except Exception as e:
        print(f"Refresh failed: {type(e).__name__}: {e}")
        return {"message": f"Failed to refresh: {e}"}