from fastapi import APIRouter, HTTPException
from app.schemas.request_schema import InputData
from app.services.ml_service import predict
from app.services.logging_service import log_predictions
import time

router = APIRouter()

@router.post("/predict")
def predict_route(data: InputData):
    try:
        if not data.text.strip():
            return HTTPException(status_code=400, detail="Input text cannot be empty.")
        
        start = time.perf_counter()
        pred, prob = predict(data.text, data.model)
        latency = time.perf_counter() - start
        log_predictions(data.text, pred, prob, data.model, latency)

        return {
            "prediction":pred,
            "confidence_scores":prob,
            "latency":latency
        }
    except Exception as e:
        return {"error": str(e)}