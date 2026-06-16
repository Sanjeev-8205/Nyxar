from fastapi import APIRouter
from app.core.database import SessionLocal
from sqlalchemy import text

router = APIRouter()

@router.get("/db_status")
def db_status_check():
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