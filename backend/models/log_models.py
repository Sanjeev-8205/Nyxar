from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, UTC
from app.core.database import Base

class Log(Base):
    __tablename__ = "logs"

    id=Column(Integer, primary_key=True, index=True)
    text=Column(String)
    prediction=Column(String)
    model=Column(String)
    confidence = Column(Float)
    negative=Column(Float)
    neutral=Column(Float)
    positive=Column(Float)
    latency=Column(Float)
    status=Column(String)
    timestamp=Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))