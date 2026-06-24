from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import get_settings

load_dotenv()

settings = get_settings()

if not settings.USE_MOCK_LLM:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine=None
    SessionLocal=None

Base = declarative_base()