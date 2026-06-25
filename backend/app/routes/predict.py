from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.schemas.request_schema import InputData
from app.services.ml_service import predict
from app.services.logging_service import log_predictions
from app.services.insights_service.live_inference_insights import generate_ai_prediction_insights
import time
import asyncio
import traceback
import structlog

from app.core import prometheus_metrics as pm
from app.core.security import verify_api_key

router = APIRouter()

def log_predictions_with_metrics(text, pred, confidence, prob, model, latency, status, request_id):
    try:
        log_predictions(text, pred, confidence, prob, model, latency, status, request_id)

    except Exception as log_error:
        print(f"Logging Failed : {log_error}")

logger=structlog.get_logger()

@router.post("/predict")
async def predict_route(data: InputData, background_tasks: BackgroundTasks, _:bool=Depends(verify_api_key)):
    request_id = structlog.contextvars.get_contextvars().get("request_id")
    log = logger.bind(model=data.model, input_length=len(data.text))

    log.info("inference_request_received", has_text=bool(data.text.strip()))

    start_request = time.perf_counter()
    pm.LIVE_INFERENCE_REQUEST_COUNT.inc()

    pred = None
    prob = None
    confidence = None
    status = "failure"
    latency = 0

    try:

        if not data.text.strip():
            log.warning("inference_input_invalid", reason = "empty_text" if data.text=="" else "whitespace_only")
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")

        start_time=time.perf_counter()
        pred, prob, trace, total_time = await asyncio.to_thread(
            predict,
            data.text,
            data.model
        )
        latency = time.perf_counter() - start_time

        conf_score = max(prob)
        confidence=conf_score

        pred_map = {"0":"Negative", "1":"Neutral", "2":"Positive"}
        prediction = pred_map.get(str(pred), "Unknown")

        log.info(
            "inference_completed",
            confidence=round(conf_score, 4),
            prediction=prediction,
            duration_ms = round(latency*1000, 2)
        )

        if conf_score<0.5:
            log.warning("inference_low_confidence", prediction=prediction, confidence=round(conf_score, 4))

        pm.LIVE_INFERENCE_PREDICTION_COUNT.labels(
            model=data.model
        ).inc()

        pm.LIVE_INFERENCE_PREDICTION_LATENCY.labels(model=data.model).observe(latency)
        pm.LATENCY_BREAKDOWN.labels(latency_type = "ML_Inference").observe(latency)

        pm.MODEL_PREDICTION_CONFIDENCE.labels(
            model=data.model
        ).observe(confidence)

        pm.MODEL_PREDICTION_CONFIDENCE_GAUGE.labels(
            model=data.model
        ).set(confidence)

        status = "success"

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
        log.error("inference_failed", error=str(prediction_error), exc_info=True)
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
                data.text, pred, confidence, prob, data.model, latency, status, request_id
            )
        except Exception as e:
            log.error("inference_db_write_failed", error=str(e), exc_info=True)
            pass