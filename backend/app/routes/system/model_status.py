from fastapi import APIRouter
from app.core.model_loader import loaded_models

router = APIRouter()

@router.get("/model_status")
def check_model_status():
    return {
        "loaded_models": loaded_models
    }