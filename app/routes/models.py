from fastapi import APIRouter, Depends
from app.core.model_loader import models
from app.core.security import verify_api_key

router = APIRouter()

@router.get("/models")
def get_models(_:bool=Depends(verify_api_key)):
    return list(models.keys())