from app.core.database import Base
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, UTC

class OverviewInsights(Base):
    __tablename__ = "overview_insights"

    id = Column(Integer, primary_key=True, index=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    ai_insights = Column(JSONB)

    provider = Column(String, default='gemini-3.1-flash-lite')

    fallback_used = Column(Boolean, default=False)

    fallback_reason = Column(String, nullable=True)

    llm_latency = Column(Float, nullable=True)

    input_tokens = Column(Integer, nullable=True)

    thoughts_tokens = Column(Integer, nullable=True)

    output_tokens = Column(Integer, nullable=True)
    
    total_tokens = Column(Integer, nullable=True)

    prompt_version = Column(String)

    error = Column(Text, nullable=True)