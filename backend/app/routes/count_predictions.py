from fastapi import APIRouter
from pathlib import Path
import pandas as pd

router = APIRouter()

BASE_DIR = Path(__file__).resolve()

@router.get("/count_predictions")
def get_counts():
    log_path=BASE_DIR.parent.parent.parent / "logs" / "logs.csv"

    if not log_path.exists():
        return []

    df=pd.read_csv(log_path)

    return df["Prediction"].astype(int).tolist()
