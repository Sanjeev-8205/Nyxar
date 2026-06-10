from fastapi import APIRouter, HTTPException
from app.schemas.request_schema import InputData
from app.services.ml_service import predict
from app.services.logging_service import log_predictions
from app.services.insights_service.live_inference_insights import generate_ai_prediction_insights
import time

from app.core import prometheus_metrics as pm

router = APIRouter()

@router.post("/predict")
def predict_route(data: InputData):
    start_request = time.perf_counter()
    pm.LIVE_INFERENCE_REQUEST_COUNT.inc()

    pred = None
    prob = None
    confidence = None
    status = "failure"

    try:
        if not data.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
        start = time.perf_counter()
        pred, prob, trace, total_time = predict(data.text, data.model)
        latency = time.perf_counter() - start

        pm.LIVE_INFERENCE_PREDICTION_COUNT.inc()

        conf_score = max(prob)
        confidence=conf_score

        status = "success"
        
        pred_map = {"0":"Negative", "1":"Neutral", "2":"Positive"}
        prediction = pred_map.get(str(pred), "Unknown")

        if conf_score<0.4:
            certainty = "LOW CONFIDENCE"
        elif conf_score<0.7:
            certainty = "MODERATE CERTAINTY"
        else:
            certainty = "HIGH CERTAINTY"

        text = data.text
        words = len(text.split())
        sentences = max(
            1,
            len([s for s in text.split(".") if s.strip()])
        )

        if words<20:
            complexity = "LOW"
        elif words<60:
            complexity = "MEDIUM"
        else:
            complexity = "HIGH"

        response = generate_ai_prediction_insights(
            prediction=prediction, confidence=conf_score, prob=prob,
            word_count=words, sentence_count=sentences, complexity=complexity, text=data.text
        )

        return {
            "prediction":prediction,
            "confidence_scores":prob,
            "confidence": conf_score,
            "latency": f"{round(latency,3)*1000} ms",
            "model_used": data.model,
            "certainty": certainty,
            "total_time": total_time,
            "trace": trace,
            "words": words,
            "characters": len(text),
            "sentences": sentences,
            "complexity": complexity,
            "insight": response["insight"],
            "llm_used": response["model"]
        }

    finally:
        try:
            log_predictions(data.text, pred, confidence, prob, data.model, latency, status)
            pm.REQUEST_LATENCY.observe(round(time.perf_counter() - start_request, 4))
        except Exception as log_error:
            pm.LIVE_INFERENCE_ERROR_COUNT.inc()
            print(f"Logging Failed : {log_error}")