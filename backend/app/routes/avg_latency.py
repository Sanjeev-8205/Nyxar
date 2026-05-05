from fastapi import APIRouter
from pathlib import Path
import pandas as pd

router=APIRouter()

BASE_DIR = Path(__file__).resolve()

@router.get("/avg_latency")
def get_avg_latency():
    log_path=BASE_DIR.parent.parent.parent / "logs" / "logs.csv"

    if not log_path.exists():
        return {"data":[]}
    
    logs=pd.read_csv(log_path)

    avg_latency=logs.groupby("Model")["Latency"].mean().reset_index(name="Avg_latency")

    return avg_latency.to_dict(orient="records")