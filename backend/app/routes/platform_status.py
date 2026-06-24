from fastapi import APIRouter, Depends, HTTPException
from app.services.insights_service.platform_status_strip import get_overview_status
from app.core.database import SessionLocal
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.core.dependencies import get_db

router  =APIRouter()

@router.get("/platform_status")
def get_platform_status(
    db: Session = Depends(get_db), _:bool=Depends(verify_api_key)
):
    try:
        result = get_overview_status(db)
        print(f"Platform status result: {result}")
        return result
    except Exception as e:
        print(f"Platform status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))