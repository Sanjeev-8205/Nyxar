from app.core.model_registry import models

loaded_models={}

def get_model(name):
    if name not in models:
        raise ValueError(f"Model '{name}' not found")

    if name not in loaded_models:
        print(f"Loading {name}....")
        loaded_models[name]=models[name]['loader']()

    return loaded_models[name]