<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
=======
from fastapi import APIRouter, HTTPException, BackgroundTasks
>>>>>>> nyxar-backend/main
from app.schemas.request_schema import InputData
from app.services.ml_service import predict
from app.services.logging_service import log_predictions
from app.services.insights_service.live_inference_insights import generate_ai_prediction_insights
import time

from app.core import prometheus_metrics as pm

router = APIRouter()

<<<<<<< HEAD
@router.post("/predict")
def predict_route(data: InputData):
=======
async def log_predictions_with_metrics(text, pred, confidence, prob, model, latency, status):
        try:
            async with pm.LATENCY_BREAKDOWN.labels(latency_type = "DB_write").time():
                await log_predictions(text, pred, confidence, prob, model, latency, status)

        except Exception as log_error:
            print(f"Logging Failed : {log_error}")

@router.post("/predict")
async def predict_route(data: InputData, background_tasks: BackgroundTasks):
>>>>>>> nyxar-backend/main
    start_request = time.perf_counter()
    pm.LIVE_INFERENCE_REQUEST_COUNT.inc()

    pred = None
    prob = None
    confidence = None
    status = "failure"
<<<<<<< HEAD
=======
    latency = 0
>>>>>>> nyxar-backend/main

    try:
        if not data.text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
<<<<<<< HEAD
        start = time.perf_counter()
        pred, prob, trace, total_time = predict(data.text, data.model)
        latency = time.perf_counter() - start
=======
        start_time=time.perf_counter()
        async with pm.LIVE_INFERENCE_PREDICTION_LATENCY.labels(model=data.model).time():
            async with pm.LATENCY_BREAKDOWN.labels(latency_type = "ML_Inference").time():
                pred, prob, trace, total_time = await predict(data.text, data.model)
        latency = time.perf_counter() - start_time
>>>>>>> nyxar-backend/main

        pm.LIVE_INFERENCE_PREDICTION_COUNT.labels(
            model=data.model
        ).inc()

<<<<<<< HEAD
        pm.LIVE_INFERENCE_PREDICTION_LATENCY.labels(
            model=data.model
        ).observe(round(latency*1000), 0)

=======
>>>>>>> nyxar-backend/main
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

<<<<<<< HEAD
        response = generate_ai_prediction_insights(
            prediction=prediction, confidence=conf_score, prob=prob,
            word_count=words, sentence_count=sentences, complexity=complexity, text=data.text
        )

=======
        async with pm.LATENCY_BREAKDOWN.labels(latency_type = "llm").time():
            response = await generate_ai_prediction_insights(
                prediction=prediction, confidence=conf_score, prob=prob,
                word_count=words, sentence_count=sentences, complexity=complexity, text=data.text
            )
>>>>>>> nyxar-backend/main

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

    except Exception as prediction_error:
        pm.LIVE_INFERENCE_ERROR_COUNT.inc()
        print(f"Prediction_failed: {prediction_error}")

    finally:
<<<<<<< HEAD
        try:
            log_predictions(data.text, pred, confidence, prob, data.model, latency, status)
            pm.REQUEST_LATENCY_SINGLE_INFERENCE.labels(
                model=data.model
            ).observe(round((time.perf_counter() - start_request)*1000,0))

        except Exception as log_error:
            print(f"Logging Failed : {log_error}")
=======
        pm.REQUEST_LATENCY_SINGLE_INFERENCE.labels(
                model=data.model
            ).observe(round((time.perf_counter() - start_request)*1000,0))
        
        background_tasks.add_task(
            log_predictions_with_metrics,
            data.text, pred, confidence, prob, data.model, latency, status
        )
>>>>>>> nyxar-backend/main
