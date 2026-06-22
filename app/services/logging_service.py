from app.core.database import SessionLocal
from models.log_models import Log
import time
from app.core import prometheus_metrics as pm

def log_predictions(text, prediction, confidence, prob, model, latency, status):
    db=SessionLocal()

    try:
        db_start_time = time.perf_counter()
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
        pm.LATENCY_BREAKDOWN.labels(latency_type = "DB_write").observe(time.perf_counter() - db_start_time)

    finally:
        db.close()
