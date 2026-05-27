from fastapi import APIRouter, Depends
from app.services.insights_service.platform_status_strip import get_overview_status
from app.core.database import SessionLocal
from sqlalchemy.orm import Session

router  =APIRouter()

def get_db():
    try:
        db = SessionLocal()

        yield
    
    finally:
        db.close()

@router.get("/platform_status")
def get_platform_status(
    db: Session = Depends(get_db)
):
    return get_overview_status(db)