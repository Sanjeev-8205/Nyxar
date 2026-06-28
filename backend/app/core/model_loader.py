from app.core.model_registry import models
from fastapi import HTTPException

loaded_models={}

def get_model(name):
    if name not in models:
        raise HTTPException(status_code=422, detail="Invalid model")

    if name not in loaded_models:
        print(f"Loading {name}....")
        loaded_models[name]=models[name]['loader']()

    return loaded_models[name]