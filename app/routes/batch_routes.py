from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from models.batch_job_model import BatchJob
from models.batch_result_model import BatchResult
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.batch_service import process_batch_job
import pandas as pd
from pathlib import Path
import uuid

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()

        yield db

    finally:
        db.close()
    
@router.post("/batch/upload")
async def upload_batch_file(
    background_tasks: BackgroundTasks,
    model: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    #Validate CSV
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    up_path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR = up_path/ "upload"
    UPLOAD_DIR.mkdir(exist_ok=True)

    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    upload_path = UPLOAD_DIR / unique_filename

    with open(upload_path, "wb") as buffer:
        buffer.write(await file.read())
    
    #Validate CSV structure
    try:
        df = pd.read_csv(upload_path)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file.")

    #check required columns
    if "text" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'text' column.")

    # Create job
    job = BatchJob(
        filename=file.filename,
        status="pending",
        model_name=model,
        total_rows=len(df),
        processed_rows=0,
        progress=0.0,
        all_columns=", ".join(df.columns),
        text_column="text"
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
async def get_batch_job(job_id: int):
    db = SessionLocal()

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
            "throughput": job.throughput,
            "progress": job.progress,
            "processing_time": job.processing_time,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message
        }

    finally:
        db.close()

@router.get("/batch/job/{job_id}/results")
async def get_batch_job_results(job_id: int):
    db = SessionLocal()

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
