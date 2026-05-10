from fastapi import APIRouter
from app.services.metrics_service.dashboard_metrics_service import dashboard_metrics_aggregator

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_metrics():
    return dashboard_metrics_aggregator()