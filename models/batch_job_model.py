from sqlalchemy import Column, DateTime, String, Float, Integer, Text
from app.core.database import Base
from datetime import datetime, UTC

class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index = True)
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")

    model_name = Column(String, default="Logistic Regression")

    all_columns = Column(Text, default=[])
    text_column = Column(String, default="reviews")
    
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)

    inference_time = Column(Float, default = 0.0)
    db_time = Column(Float, default = 0.0)
    overhead_time = Column(Float, default = 0.0)

    throughput = Column(Float, default = 0.0)

    progress = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), default=lambda:datetime.now(UTC))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    error_message = Column(String, nullable=True)