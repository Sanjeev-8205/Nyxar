from sqlalchemy.orm import Session


def get_db():
    db=None
    try:
        from app.core import database
        db = database.SessionLocal()

        yield db

    finally:
        if db is not None:
            db.close()