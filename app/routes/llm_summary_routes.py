from fastapi import APIRouter, Depends
from app.services.llm_service import generate_ai_summary
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from models.batch_summary_model import BatchSummary
from models.batch_result_model import BatchResult
from models.batch_job_model import BatchJob
from sqlalchemy import func

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

    pred_dist=(
        db.query(BatchResult.prediction.label("sentiment"),
        func.count(BatchResult.id).label("countings"))
        .filter(BatchResult.job_id == job_id)
        .group_by(BatchResult.prediction)
        .order_by(BatchResult.prediction.desc()).all()
    )

    dataset_context = (
        db.query(BatchJob.filename.label("filename"), BatchJob.all_columns.label("no_of_columns"),
            BatchJob.text_column.label("text_column"), BatchJob.total_rows.label("total_rows"),
            BatchJob.model_name.label("model_name")).first()
    )

    if existing_summary:
        return {
            "cached": True,
            "summary": existing_summary.summary,
            "sections": existing_summary.summary.get("sections"),
            "recommendations": existing_summary.summary.get("recommendations"),
            "risk_assessment": existing_summary.summary.get("risk_assessment"),
            "confidence_assessment": existing_summary.summary.get("confidence_assessment"),
            "opportunity_assessment": existing_summary.summary.get("opportunity_assessment"),
            "report_metadata": existing_summary.summary.get("report_metadata"),
            "provider": existing_summary.provider,
            "latency": existing_summary.llm_latency,
            "summary_type": existing_summary.summary_type
        }

    sentiments_mapping = {"0": "Negative", "1": "Neutral", "2": "Positive"}
    pred_distribution = {
        sentiments_mapping[row.sentiment]: row.countings
        for row in pred_dist
    }

    negative_reviews = get_top("0", job_id, db)
    neutral_reviews = get_top("1", job_id, db)
    positive_reviews = get_top("2", job_id, db)

    results = generate_ai_summary(
        positive_reviews = positive_reviews,
        neutral_reviews = neutral_reviews,
        negative_reviews = negative_reviews,
        summary_type = summary_type,
        prediction_distribution=pred_distribution,
        dataset_context={
            "filename": dataset_context.filename,
            "no_of_columns": dataset_context.no_of_columns,
            "review_column_name": dataset_context.text_column,
            "total_rows": dataset_context.total_rows,
            "model_name": dataset_context.model_name
        }
    )

    summary = results["summary"]
    print(f"AI response keys: {summary.keys()}")

    new_summary = BatchSummary(
        job_id = job_id,
        summary_type = summary_type,
        summary = summary,
        provider = results["provider"],
        fallback_used = results["fallback_used"],
        llm_latency = results["latency"],
        estimated_token = results["estimated_tokens"],
        input_tokens = results["input_tokens"],
        output_tokens = results["output_tokens"],
        total_tokens = results["total_tokens"],
        thoughts_tokens= results["thoughts_tokens"],
        prompt_version = results["prompt_version"],
        error = results["error"]
    )

    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    return {
        "cached": False,
        "summary": summary.get("executive_summary"),
        "sections": summary.get("sections"),
        "recommendations": summary.get("recommendations"),
        "risk_assessment": summary.get("risk_assessment"),
        "confidence_assessment": summary.get("confidence_assessment"),
        "opportunity_assessment": summary.get("opportunity_assessment"),
        "report_metadata": summary.get("report_metadata"),
        "provider": results["provider"],
        "latency": results["latency"],
        "summary_type": results["summary_type"]
    }