from sqlalchemy.orm import Session
from sqlalchemy import insert
from app.core.database import SessionLocal
from models.batch_job_model import BatchJob
from models.batch_result_model import BatchResult
from app.services.ml_service import predict_batch
from app.services.insights_service.live_inference_insights import generate_batch_prediction_ai_insights

import pandas as pd
import time
from datetime import datetime, UTC

def process_batch_job(job_id: int, file_path: str, model:str):
    db = SessionLocal()

    try:
        job = db.query(BatchJob).filter(BatchJob.id == job_id).first()

        if not job:
            return

        #mark processing
        job.status = "Processing"
        db.commit()

        operational_start = time.perf_counter()
        #Read CSV
        df = pd.read_csv(file_path)

        total_rows = len(df)

        start = time.perf_counter()
        preds, probs, trace = predict_batch(df["text"], model)
        ml_processing_time = time.perf_counter() - start

        job.ml_processing_time = ml_processing_time
        job.throughput = total_rows/ml_processing_time
        
        try:
            if len(trace)==4 and model == "Bi-LSTM":
                for x in range(len(trace)):
                    if x==0:
                        job.text_preprocessing_time = trace[x]["time_taken"]
                    elif x==1:
                        job.tokenization_time = trace[x]["time_taken"]
                    elif x==2:
                        job.sequence_padding_time = trace[x]["time_taken"]
                    else:
                        job.inference_time = trace[x]["time_taken"]

            elif len(trace)==3 and model == "Logistic Regression":
                for x in range(len(trace)):
                    if x==0:
                        job.text_preprocessing_time = trace[x]["time_taken"]
                    elif x==1:
                        job.vectorization_time = trace[x]["time_taken"]
                    else:
                        job.inference_time = trace[x]["time_taken"]
            
            elif len(trace==3) and model == "RoBERTa Transformer":
                for x in range(len(trace)):
                    if x==0:
                        job.text_preprocessing_time = trace[x]["time_taken"]
                    elif x==1:
                        job.tokenization_time = trace[x]["time_taken"]
                    else :
                        job.inference_time = trace[x]["time_taken"]
        
        except Exception as trace_error:
            raise RuntimeError(f"Trace Error: {trace_error}")

        BUFFER = max(1, total_rows//10)
        db_time = 0
        results_buffer=[]
        for index, (text, pred, prob) in enumerate(zip(df["text"], preds, probs)):
            results_buffer.append({
                "job_id": job.id,
                "text": text,
                "prediction": pred,
                "confidence": float(max(prob)),
                "model_used": job.model_name
            })

            if len(results_buffer) >= BUFFER:
                st_time = time.perf_counter()
                stmt = insert(BatchResult).values(results_buffer)
                db.execute(stmt)
                db.flush()
                db_time += time.perf_counter() - st_time

                results_buffer.clear()

                job.processed_rows = index + 1
                job.progress = round(
                    ((index+1)/total_rows)*100, 2
                )

                proc_time = time.perf_counter() - operational_start
                job.processing_time = round(proc_time, 4)

                st_time = time.perf_counter()
                db.commit()
                db_time += time.perf_counter() - st_time

        if results_buffer:
            st_time = time.perf_counter()
            stmt = insert(BatchResult).values(results_buffer)
            db.execute(stmt)
            db.flush()
            db_time += time.perf_counter() - st_time

        end_time = time.perf_counter()

        job.status = "completed"

        proc_time = end_time - operational_start
        job.processing_time = round(proc_time, 4)
        job.completed_at = datetime.now(UTC)
        job.processed_rows = total_rows
        job.progress = 100
        job.db_time = round(db_time, 4)
        job.overhead_time = round(proc_time - db_time - ml_processing_time, 4)

        completion_rate = (job.processed_rows/job.total_rows) if job.total_rows>0 else 0
        
        job.ai_insights = generate_batch_prediction_ai_insights(
            total_rows=job.total_rows, processed_rows=job.processed_rows, completion_rate=round(completion_rate*100, 2),
            throughput=job.throughput, ml_processing_time=job.ml_processing_time, database_time=job.db_time,
            overhead_time=job.overhead_time, total_runtime=(job.completed_at - job.created_at).total_seconds(),
            ml_model_used=job.model_name
        )

        db.commit()

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()

    finally:
        db.close()