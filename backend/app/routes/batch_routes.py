from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from models.batch_job_model import BatchJob
from models.batch_result_model import BatchResult
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.services.batch_service import process_batch_job
from datetime import datetime, UTC
import pandas as pd
from pathlib import Path
import uuid
import time

from app.services.insights_service.live_inference_insights import generate_batch_prediction_ai_insights
from app.core.security import verify_api_key
from app.core.dependencies import get_db

router = APIRouter()

@router.post("/batch/upload")
async def upload_batch_file(
    background_tasks: BackgroundTasks,
    model: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _:bool=Depends(verify_api_key)
):
    created_at = datetime.now(UTC)

    #Validate CSV
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    up_path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR = up_path/ "upload"
    UPLOAD_DIR.mkdir(exist_ok=True)

    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    upload_path = UPLOAD_DIR / unique_filename

    st = time.perf_counter()
    with open(upload_path, "wb") as buffer:
        buffer.write(await file.read())
    upload_time = time.perf_counter() - st

    start = time.perf_counter()
    #Validate CSV structure
    try:
        df = pd.read_csv(upload_path)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file.")

    #check required columns
    if "text" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'text' column.")

    end_time = time.perf_counter() - start

    # Create job
    job = BatchJob(
        filename=file.filename,
        status="pending",
        model_name=model,
        total_rows=len(df),
        processed_rows=0,
        progress=0.0,
        all_columns=len(df.columns),
        text_column="text",
        file_validation_time = end_time,
        upload_time = upload_time,
        created_at = created_at
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(
        process_batch_job,
        job.id,
        upload_path,
        model
    )

    return {
        "message": "Batch job created",
        "job_id": job.id,
        "total_rows": len(df),
        "status": "pending"
    }

@router.get("/batch/job/{job_id}")
async def get_batch_job(job_id: int, _:bool=Depends(verify_api_key), db:Session = Depends(get_db)):

    try:
        job = db.query(BatchJob).filter(BatchJob.id == job_id).first()

        if not job:
            raise HTTPException(status_code=404, detail = "Job Not Found")
        
        
        
        return {
            "job_id": job.id,
            "filename": job.filename,
            "status": job.status,
            "model_name": job.model_name,
            "all_columns":job.all_columns,
            "text_column":job.text_column,
            "total_rows": job.total_rows,
            "processed_rows": job.processed_rows,
            "inference_time": job.inference_time,
            "ml_processing_time": job.ml_processing_time,
            "db_time": job.db_time,
            "overhead_time": job.overhead_time,
            "upload_time": job.upload_time,
            "validation_time": job.file_validation_time,
            "text_preprocessing_time": job.text_preprocessing_time,
            "vectorization_time": job.vectorization_time,
            "tokenization_time": job.tokenization_time,
            "sequence_padding_time": job.sequence_padding_time,
            "throughput": job.throughput,
            "progress": job.progress,
            "processing_time": job.processing_time,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message,
            "insight": job.ai_insights
        }

    finally:
        db.close()

@router.get("/batch/job/{job_id}/results")
async def get_batch_job_results(job_id: int, _:bool=Depends(verify_api_key), db:Session = Depends(get_db)):

    try:
        results = (
            db.query(BatchResult).filter(BatchResult.job_id == job_id).all()
        )

        if not results:
            raise HTTPException(status_code=404, detail="No results found for this job.")
    
        formatted_results = []

        for result in results:
            formatted_results.append({
                "text": result.text,
                "prediction": result.prediction,
                "confidence": result.confidence,
                "model_used": result.model_used
            })
        
        return {
            "job_id": job_id,
            "total_results": len(formatted_results),
            "results": formatted_results
        }

    finally:
        db.close()