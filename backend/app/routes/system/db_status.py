from fastapi import APIRouter, Depends
from app.core.database import SessionLocal
from sqlalchemy import text

from app.core.security import verify_api_key

router = APIRouter()

@router.get("/db_status")
def db_status_check(_:bool=Depends(verify_api_key)):
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }
    
    except Exception as e:
        return{
            "database": "disconnected",
            "error": str(e)
        }

    finally:
        db.close()