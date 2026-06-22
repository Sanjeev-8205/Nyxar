from fastapi import APIRouter, Depends
from app.core.model_loader import loaded_models
from app.core.security import verify_api_key

router = APIRouter()

@router.get("/model_status")
def check_model_status(_:bool=Depends(verify_api_key)):
    return {
        "loaded_models":list(loaded_models.keys())
    }