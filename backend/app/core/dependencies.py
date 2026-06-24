from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def get_db():
    db=None
    try:
        db = SessionLocal()

        yield db

    finally:
        if db is not None:
            db.close()