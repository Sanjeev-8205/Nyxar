from fastapi import APIRouter, Depends
from app.services.llm_service import generate_ai_summary
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from models.batch_summary_model import BatchSummary
from models.batch_result_model import BatchResult

router = APIRouter()

def get_db():
    try:
        db = SessionLocal()

        yield db

    finally:
        db.close()

def get_top(sentiment, job_id, db):
    results = db.query(
        BatchResult.text, 
        BatchResult.prediction, 
        BatchResult.confidence
    ).filter(
        BatchResult.job_id == job_id, 
        BatchResult.prediction == sentiment
    ).order_by(BatchResult.confidence.desc()).limit(50).all()

    return results

@router.get("/batch/job/{job_id}/summary")
def generate_summary(
    job_id: int,
    summary_type: str="full",
    db: Session = Depends(get_db)
):
    existing_summary = db.query(BatchSummary).filter(
        BatchSummary.job_id == job_id,
        BatchSummary.summary_type == summary_type
    ).first()

    if existing_summary:
        return {
            "cached": True,
            "summary": existing_summary.summary,
            "provider": existing_summary.provider,
            "latency": existing_summary.llm_latency,
            "summary_type":existing_summary.summary_type
        }

    negative_reviews = get_top("0", job_id, db)
    neutral_reviews = get_top("1", job_id, db)
    positive_reviews = get_top("2", job_id, db)

    results = generate_ai_summary(
        positive_reviews = positive_reviews,
        neutral_reviews = neutral_reviews,
        negative_reviews = negative_reviews,
        summary_type = summary_type
    )

    new_summary = BatchSummary(
        job_id = job_id,
        summary_type = summary_type,
        summary = results["summary"],
        provider = results["provider"],
        fallback_used = results["fallback_used"],
        llm_latency = results["latency"],
        estimated_token = results["estimated_tokens"],
        input_tokens = results["input_tokens"],
        output_tokens = results["output_tokens"],
        total_tokens = results["total_tokens"],
        prompt_version = results["prompt_version"],
        error = results["error"]
    )

    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    return {
        "cached": False,
        "summary": results["summary"],
        "provider": results["provider"],
        "latency": results["latency"],
        "summary_type": results["summary_type"]
    }