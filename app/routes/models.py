from fastapi import APIRouter
from app.core.model_loader import models

router = APIRouter()

@router.get("/models")
def get_models():
    return list(models.keys())