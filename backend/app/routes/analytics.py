from fastapi import APIRouter
from pathlib import Path
import pandas as pd

router = APIRouter()

BASE_DIR = Path(__file__).resolve()

@router.get("/analytics")
def get_analytics():
    log_path = BASE_DIR.parent.parent.parent / "logs" / "logs.csv"

    if not log_path.exists():
        return []
    
    df=pd.read_csv(log_path)

    avg_scores={
        "Negative":float(df["Negative"].mean()),
        "Neutral":float(df["Neutral"].mean()),
        "Positive":float(df["Positive"].mean())
    }

    return avg_scores