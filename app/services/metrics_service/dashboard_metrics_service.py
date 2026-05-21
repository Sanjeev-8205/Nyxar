from app.core.database import SessionLocal
from app.services.metrics_service.inference_metrics_service import get_inference_metrics
import app.services.metrics_service.analytics_metrics_service as analytics_ms
import app.services.metrics_service.health_metrics_service as health_ms
import app.services.metrics_service.advanced_metrics_service as adv_ms
import app.services.metrics_service.logs_metrics_service as logs_ms
import traceback

def dashboard_metrics_aggregator():
    db = SessionLocal()

    try:
        return {
            "inference": get_inference_metrics(db),
            "health":{
                "db_health": health_ms.db_health_check(db),
                "models_count": health_ms.loaded_models_count(),
                "uptime": health_ms.get_uptime(),
                "cpu_usage": health_ms.get_cpu_usage(),
                "ram_usage": health_ms.get_ram_usage()
            },
            "analytics":{
                "sentiment_distribution": analytics_ms.get_sentiment_distribution(db),
                "predictions_over_time": analytics_ms.get_predictions_over_time(db),
                "model_usage_distribution": analytics_ms.get_model_usage_distribution(db),
                "latency_trends": analytics_ms.get_latency_trends(db),
                "confidence_distribution": analytics_ms.get_confidence_distribution(db),
                "recent_activity": analytics_ms.get_recent_activity_feed(db),
                "throughput_per_hour": analytics_ms.get_throughput_per_hour(db)
            },
            "advanced":{
                "p95_latency": adv_ms.get_p95_latency(db),
                "failure_rate": adv_ms.get_failure_percent(db),
                "model_metrics":adv_ms.get_model_metrics(),
                "latency_per_model": adv_ms.get_avg_latency_per_model(db),
                "drift_indicators":adv_ms.get_drift_indicators(db)
            },
            "logs": logs_ms.get_logs(db)
        }
    
    except Exception as e:
        return {
            "error": traceback.format_exc()
        }

    finally:
        db.close()