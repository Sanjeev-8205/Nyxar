from app.core.database import SessionLocal
from app.core.model_loader import loaded_models
from app.core.app_startup import app_startup_time
from sqlalchemy import text
from datetime import datetime, UTC
import psutil

def db_health_check(db):
    try:
        db.execute(text("SELECT 1"))

        return{
            "database": "connected"
        }
    
    except Exception:
        return {
            "database": "disconnected"
        }

def loaded_models_count():
    return len(loaded_models.keys())

def get_uptime():
    uptime = datetime.now(UTC)-app_startup_time

    total_seconds = uptime.total_seconds()
    hours = int(total_seconds/3600)
    minutes = int((total_seconds%3600)/60)

    return f"{hours}h {minutes}m"

def get_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1)

    if cpu_usage<70:
        status = "Safe"
    elif cpu_usage<90:
        status = "Warning"
    else:
        status = "Critical"
    
    return [cpu_usage, status]