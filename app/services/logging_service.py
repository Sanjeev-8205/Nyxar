from app.core.database import SessionLocal
from models.log_models import Log

def log_predictions(text, prediction, confidence, prob, model, latency, status):
    db=SessionLocal()

    try:
        logs=Log(
            text=text,
            prediction=prediction,
            model=model,
            confidence=confidence,
            negative=prob[0],
            neutral=prob[1],
            positive=prob[2],
            latency=latency,
            status=status
        )

        db.add(logs)
        db.commit()

    finally:
        db.close()