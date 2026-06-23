from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.schemas.request_schema import InputData
from app.services.ml_service import predict
from app.services.logging_service import log_predictions
from app.services.insights_service.live_inference_insights import generate_ai_prediction_insights
import time
import asyncio
import traceback

from app.core import prometheus_metrics as pm
from app.core.security import verify_api_key

router = APIRouter()

def log_predictions_with_metrics(text, pred, confidence, prob, model, latency, status):
    try:
        log_predictions(text, pred, confidence, prob, model, latency, status)

    except Exception as log_error:
        print(f"Logging Failed : {log_error}")

@router.post("/predict")
async def predict_route(data: InputData, background_tasks: BackgroundTasks, _:bool=Depends(verify_api_key)):
    start_request = time.perf_counter()
    pm.LIVE_INFERENCE_REQUEST_COUNT.inc()

    pred = None
    prob = None
    confidence = None
    status = "failure"
    latency = 0

    try:
        if not data.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
        start_time=time.perf_counter()
        pred, prob, trace, total_time = await asyncio.to_thread(
            predict,
            data.text,
            data.model
        )
        latency = time.perf_counter() - start_time

        pm.LIVE_INFERENCE_PREDICTION_COUNT.labels(
            model=data.model
        ).inc()

        pm.LIVE_INFERENCE_PREDICTION_LATENCY.labels(model=data.model).observe(latency)
        pm.LATENCY_BREAKDOWN.labels(latency_type = "ML_Inference").observe(latency)

        conf_score = max(prob)
        confidence=conf_score

        pm.MODEL_PREDICTION_CONFIDENCE.labels(
            model=data.model
        ).observe(confidence)

        pm.MODEL_PREDICTION_CONFIDENCE_GAUGE.labels(
            model=data.model
        ).set(confidence)

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

        response = await generate_ai_prediction_insights(
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

    except Exception:
        raise

    except Exception as prediction_error:
        pm.LIVE_INFERENCE_ERROR_COUNT.inc()
        
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(prediction_error)
        )

    finally:
        try:
            pm.REQUEST_LATENCY_SINGLE_INFERENCE.labels(
                model=data.model
            ).observe(round((time.perf_counter() - start_request)*1000,0))
            
            background_tasks.add_task(
                log_predictions_with_metrics,
                data.text, pred, confidence, prob, data.model, latency, status
            )
        except Exception:
            pass