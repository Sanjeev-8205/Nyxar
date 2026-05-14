from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base
from models.batch_job_model import BatchJob

class BatchResult(Base):
    __tablename__ = "batch_results"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("batch_jobs.id")
    )

    text = Column(String)

    prediction = Column(String)

    confidence = Column(Float)

    model_used = Column(String)