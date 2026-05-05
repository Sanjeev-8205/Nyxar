from fastapi import APIRouter
from pathlib import Path
import pandas as pd

router = APIRouter()

BASE_DIR = Path(__file__).resolve()

@router.get("/logs")
def get_logs():
    log_path = BASE_DIR.parent.parent.parent / "logs" / "logs.csv"

    if not log_path.exists():
        return []
    
    df=pd.read_csv(log_path)
    return df.tail(5).fillna("").to_dict(orient="records")