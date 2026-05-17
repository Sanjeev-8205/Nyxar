from app.core.database import Base
from sqlalchemy import Column, Float, String, Text, DateTime, Boolean, Integer, UniqueConstraint, ForeignKey
from datetime import datetime, UTC

class BatchSummary(Base):
    __tablename__ = "batch_summaries"

    id = Column(Float, primary_key=True, index=True)

    job_id = Column(Float, ForeignKey("batch_jobs.id"))

    summary_type = Column(String, default="full")

    summary = Column(Text)

    provider = Column(String)

    fallback_used = Column(Boolean, default=False)

    llm_latency = Column(Float, nullable=True)

    estimated_token = Column(Integer, nullabel=True)

    prompt_version = Column(String, default="v1")

    error = Column(Text, nullable=True)

    created_at = Column(DateTime, default = lambda: datetime.now(UTC))

    __tableargs__ = UniqueConstraint(
        "job_id", "summary_type", name="unique_job_summary_type"
    )