from fastapi import APIRouter
from app.core.model_loader import models
from app.core import prometheus_metrics as pm

router = APIRouter()

@router.get("/models")
def get_models():
    pm.ACTIVE_MODELS.set(len(list(models.keys())))
    return list(models.keys())