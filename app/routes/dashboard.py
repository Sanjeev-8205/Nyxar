from fastapi import APIRouter, Depends
from app.services.metrics_service.dashboard_metrics_service import dashboard_metrics_aggregator
from app.core.security import verify_api_key

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_metrics(_:bool=Depends(verify_api_key)):
    return dashboard_metrics_aggregator()