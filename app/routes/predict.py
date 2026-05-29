from fastapi import APIRouter, HTTPException
from app.schemas.request_schema import InputData
from app.services.ml_service import predict
from app.services.logging_service import log_predictions
import time

router = APIRouter()

@router.post("/predict")
def predict_route(data: InputData):
    pred = None
    prob = None
    confidence = None
    status = "failure"

    try:
        if not data.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
        start = time.perf_counter()
        pred, prob = predict(data.text, data.model)
        latency = time.perf_counter() - start

        conf_score = max(prob)

        status = "success"
        
        pred_map = {"0":"Negative", "1":"Neutral", "2":"Positive"}
        prediction = pred_map.get(str(pred), "Unknown")

        if conf_score<0.4:
            severity = "High"
            certainty = "LOW CONFIDENCE"
        elif conf_score<0.7:
            severity = "Medium"
            certainty = "MODERATE CERTAINTY"
        else:
            severity = "Low"
            certainty = "HIGH CERTAINTY"

        return {
            "prediction":prediction,
            "confidence_scores":prob,
            "confidence": conf_score,
            "latency": f"{round(latency,3)*1000} ms",
            "model_used": data.model,
            "severity": severity,
            "certainty": certainty
        }

    finally:
        try:
            log_predictions(data.text, pred, confidence, prob, data.model, latency, status)
        except Exception as log_error:
            print(f"Logging Failed : {log_error}")