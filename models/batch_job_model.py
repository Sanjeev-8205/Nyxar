from sqlalchemy import Column, DateTime, String, Float, Integer, Text
from app.core.database import Base
from datetime import datetime, UTC
from sqlalchemy.dialects.postgresql import JSON

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

    file_validation_time = Column(Float, default = 0.0)
    upload_time = Column(Float, default = 0.0)
    inference_time = Column(Float, default = 0.0)
    ml_processing_time = Column(Float, default = 0.0)
    db_time = Column(Float, default = 0.0)
    overhead_time = Column(Float, default = 0.0)

    text_preprocessing_time = Column(Float, default = 0.0)
    tokenization_time = Column(Float, default = 0.0)
    vectorization_time = Column(Float, default = 0.0)
    sequence_padding_time = Column(Float, default = 0.0)

    throughput = Column(Float, default = 0.0)

    progress = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)

    ai_insights = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda:datetime.now(UTC))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    error_message = Column(String, nullable=True)