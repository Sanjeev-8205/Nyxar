from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from models.batch_job_model import BatchJob
from models.batch_result_model import BatchResult
from app.services.ml_service import predict

import pandas as pd
import time
from datetime import datetime, UTC

def process_batch_job(job_id: int, file_path: str):
    db = SessionLocal()

    try:
        job = db.query(BatchJob).filter(BatchJob.id == job_id).first()

        if not job:
            return
    
        #mark processing
        job.status = "Processing"
        db.commit()

        #Read CSV
        df = pd.read_csv(file_path)

        total_rows = len(df)
        
        start_time = time.perf_counter()

        # Process each row
        for index, row in df.iterrows():
            text = row["text"]

            try:
                start = time.time()

                pred, prob = predict(text, "Logistic Regression")

                latency = time.time() - start

                batch_result = BatchResult(
                    job_id=job.id,
                    text=text,
                    prediction=pred,
                    confidence=max(prob),
                    model_used=job.model_name,
                    latency=round(latency, 4)
                )

                db.add(batch_result)

            except Exception:

                batch_result = BatchResult(
                    job_id=job.id,
                    text=text,
                    prediction="error",
                    confidence=0,
                    model_used=job.model_name,
                    latency=0
                )

                db.add(batch_result)
        
            job.processed_rows = index + 1
            job.progress = round(
                ((index+1)/total_rows)*100, 2
            )

            db.commit()

        end_time = time.perf_counter()

        job.status = "completed"

        job.processing_time = round(end_time - start_time, 4)
        job.completed_at = datetime.now(UTC)

        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()

    finally:
        db.close()
