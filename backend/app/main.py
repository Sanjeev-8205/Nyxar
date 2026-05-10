from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.models import router as models_router
from app.routes.analytics import router as analytics_router
from app.routes.count_predictions import router as counts_router
from app.routes.predict import router as prediction_router
from app.routes.avg_latency import router as latency_router
from app.routes.system.health import router as health_router
from app.routes.system.db_status import router as db_status_router
from app.routes.system.model_status import router as model_status_router
from app.routes.dashboard import router as dashboard_router
from app.services.warmup_service import preload_models, warmup
import threading

from app.core.database import Base, engine
from models.log_models import Log

@asynccontextmanager
async def lifespan(app: FastAPI):
    def run():
        preload_models()
        warmup()

    threading.Thread(target=run, daemon=True).start()

    yield

app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

app.include_router(models_router)
app.include_router(prediction_router)
app.include_router(analytics_router)
app.include_router(counts_router)
app.include_router(latency_router)

app.include_router(health_router)
app.include_router(db_status_router)
app.include_router(model_status_router)
app.include_router(dashboard_router)

@app.get("/")
def home():
    return {"message": "API Running"}