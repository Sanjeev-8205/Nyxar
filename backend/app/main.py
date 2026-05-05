from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.models import router as models_router
from app.routes.logs import router as logs_router
from app.routes.analytics import router as analytics_router
from app.routes.count_predictions import router as counts_router
from app.routes.predict import router as prediction_router
from app.routes.avg_latency import router as latency_router
from app.services.warmup_service import preload_models, warmup
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    def run():
        preload_models()
        warmup()

    threading.Thread(target=run, daemon=True).start()

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(models_router)
app.include_router(prediction_router)
app.include_router(logs_router)
app.include_router(analytics_router)
app.include_router(counts_router)
app.include_router(latency_router)

@app.get("/")
def home():
    return {"message": "API Running"}