from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.models import router as models_router
from app.routes.predict import router as prediction_router
from app.routes.system.health import router as health_router
from app.routes.system.db_status import router as db_status_router
from app.routes.system.model_status import router as model_status_router
from app.routes.batch_routes import router as batch_router
from app.routes.dashboard import router as dashboard_router
from app.services.warmup_service import preload_models, warmup
import threading
import subprocess

from app.core.database import Base, engine
from models.log_models import Log
from models.batch_job_model import BatchJob
from models.batch_result_model import BatchResult

@asynccontextmanager
async def lifespan(app: FastAPI):
    def run():
        preload_models()
        warmup()

    t = threading.Thread(target=run)
    t.start()
    t.join()

    yield

app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

app.include_router(models_router)
app.include_router(prediction_router)

app.include_router(health_router)
app.include_router(db_status_router)
app.include_router(model_status_router)
app.include_router(dashboard_router)
app.include_router(batch_router)

@app.get("/")
def home():
    return {"message": "API Running"}

@app.get("/debug/region")
async def get_region():
    result = subprocess.run(['curl', 'https://ipinfo.io'], 
                          capture_output=True, text=True)
    return result.stdout