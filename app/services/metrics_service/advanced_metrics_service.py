from models.log_models import Log
from pathlib import Path
from sqlalchemy import func
from collections import Counter
import json
import pandas as pd
import numpy as np

def get_p95_latency(db):
    p95_latency = db.query(
        func.percentile_cont(0.95)
        .within_group(Log.latency)
    ).scalar()

    return round(float(p95_latency or 0), 3)

def get_failure_percent(db):
    status_ = db.query(
        Log.status.label("status"),
        func.count(Log.status).label("count")
    ).group_by(Log.status).all()

    total = sum(count for _, count in status_)

    failure_count = next(
        (count for status, count in status_ if status == "failure"),0)

    failure_percent = (
        (failure_count / total) * 100
        if total > 0 else 0
    )

    return {
        "failure_percent":failure_percent,
        "failure_count":failure_count,
        "total_requests":total
    }

def get_model_metrics():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    logistic_path = BASE_DIR / "metrics" / "logistic_regression.json"
    bilstm_path = BASE_DIR / "metrics" / "bilstm.json"
    bert_path = BASE_DIR/ "metrics" / "bert_base_uncased.json"

    with open(logistic_path, 'r') as f:
        logistic_metrics = json.load(f)
    
    with open(bilstm_path, 'r') as f:
        bilstm_metrics = json.load(f)
    
    with open(bert_path, 'r') as f:
        bert_metrics = json.load(f)

    models = {
        "Logistic Regression":logistic_metrics, 
        "Bi-LSTM":bilstm_metrics, 
        "BERT Transformer":bert_metrics
    }

    filtered_models = {
        model:{
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1_score": metrics["f1-score"]
        }
        for model, metrics in models.items()
    }

    return filtered_models

def get_avg_latency_per_model(db):
    avg_latency_per_model = db.query(
        Log.model.label("model"),
        func.avg(Log.latency).label("avg_latency")
    ).group_by("model").all()

    avg_latency = [
        {
            "model": model,
            "avg_latency": avg_lt
        }
        for model, avg_lt in avg_latency_per_model
    ]

    return avg_latency

def get_drift_indicators(db):
    metrics = db.query(
        Log.text.label("text"),
        Log.prediction.label("prediction"),
        func.greatest(Log.negative, Log.neutral, Log.positive).label("confidence_score"),
        Log.timestamp.label("timestamp")
    ).order_by(Log.timestamp.asc()).all()

    drift_metrics = {
        "text": [],
        "predictions": [],
        "confidence_scores": [],
        "timestamp": []
    }
    for row in metrics:
        drift_metrics["text"].append(len(row[0].split()))
        drift_metrics["predictions"].append(row[1])
        drift_metrics["confidence_scores"].append(row[2])
        drift_metrics["timestamp"].append(row[3])

    # Prediction distribution
    pred_counts = Counter(drift_metrics["predictions"])

    total = len(drift_metrics["predictions"])

    if total==0:
        return {
            "text_length_drift": [],
            "confidence_score_drift": [],
            "timestamp": []
        }
    
    #Text Length rolling window
    text_length = drift_metrics["text"]
    window_1 = min(20, len(text_length))
    rolling_text_length = (
        pd.Series(text_length)
        .rolling(window_1, min_periods=1)
        .mean()
    ).to_list()

    #Sentiment Score rolling window
    sentiments = drift_metrics["predictions"]
    pred_map = {"0":-1, "1":0, "2":1}
    sentiment_scores = [pred_map.get(s,0) for s in sentiments]
    window_3 = min(20, len(sentiment_scores))
    rolling_sentiment = (
        pd.Series(sentiment_scores)
        .rolling(window_3, min_periods=1)
        .mean()
    ).to_list()

    #Confidence Score rolling window
    conf_scores = drift_metrics["confidence_scores"]
    window_2 = min(20, len(conf_scores))
    rolling_confidence = (
        pd.Series(conf_scores)
        .rolling(window_2, min_periods=1)
        .mean()
    ).to_list()

    #Text Length Shift
    shift_window = min(50, len(text_length)//2)

    if shift_window == 0:
        return {
            "text_length_rolling": rolling_text_length,
            "sentiment_score_rolling": rolling_sentiment,
            "confidence_score_rolling": rolling_confidence,
            "text_len_shift": 0,
            "sentiment_shift": 0,
            "confidence_shift": 0,
            "timestamp": drift_metrics["timestamp"]
        }
    
    recent_text_length = text_length[-shift_window:]
    previous_text_length = text_length[-2*shift_window:-shift_window]
    tx_len_shift = (
        np.mean(recent_text_length) - np.mean(previous_text_length)
    )

    #Sentiment Score shift
    recent_sentiment = sentiment_scores[-shift_window:]
    previous_sentiment = sentiment_scores[-2*shift_window:-shift_window]
    sentiment_shift = (
        np.mean(recent_sentiment) - np.mean(previous_sentiment)
    )

    #Confidence Score Shift
    recent_confidence = conf_scores[-shift_window:]
    previous_confidence = conf_scores[-2*shift_window:-shift_window]
    confidence_shift = (
        np.mean(recent_confidence) - np.mean(previous_confidence)
    )

    return {
        "text_length_rolling": rolling_text_length,
        "sentiment_score_rolling": rolling_sentiment,
        "confidence_score_rolling": rolling_confidence,
        "text_len_shift": tx_len_shift,
        "sentiment_shift": sentiment_shift,
        "confidence_shift": confidence_shift,
        "timestamp": drift_metrics["timestamp"]
    }

def get_latency_and_throughput_shifts(db):
    metrics = db.query(
        Log.latency.label("latency"),
        (1/Log.latency).label("throughput")
    ).all()

    shift_metrics = {
        "latencies": [],
        "throughput": []
    }

    for row in metrics:
        shift_metrics["latencies"].append(row[0])
        shift_metrics["throughput"].append(row[1])

    shift_window = min(10, len(shift_metrics["latencies"]))

    if shift_window==0:
        return {
            "latency_shift": 0,
            "throughput_shift": 0
        }

    recent_latencies = shift_metrics["latencies"][-shift_window:]
    previous_latencies = shift_metrics["latencies"][-2*shift_window:-shift_window]
    latency_shift = (
        (np.mean(recent_latencies) - np.mean(previous_latencies)) / np.mean(previous_latencies) * 100
    ) if np.mean(previous_latencies) > 0 else 0

    recent_throughput = shift_metrics["throughput"][-shift_window:]
    previous_throughput = shift_metrics["throughput"][-2*shift_window:-shift_window]
    throughput_shift = (
        (np.mean(recent_throughput) - np.mean(previous_throughput)) / np.mean(previous_throughput) * 100
    ) if np.mean(previous_throughput) > 0 else 0

    return {
        "latency_shift": latency_shift,
        "throughput_shift": throughput_shift
    }