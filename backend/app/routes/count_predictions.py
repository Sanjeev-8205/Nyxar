from fastapi import APIRouter
from app.core.database import SessionLocal
from models.log_models import Log

router = APIRouter()

@router.get("/count_predictions")
def get_counts():
    db = SessionLocal()

    try:
        prediction = db.query(Log.prediction)

        prediction_list = [p[0] for p in prediction]
        
        sentiment = {
            "0": "Negative",
            "1": "Neutral",
            "2": "Positive"
        }

        predictions = [sentiment[p] for p in prediction_list]
        return predictions

    finally:
        db.close()