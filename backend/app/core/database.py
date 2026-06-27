from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import get_settings
import structlog

logger=structlog.get_logger()
load_dotenv()

settings = get_settings()

class DatabaseSessionError(Exception):
    pass

try:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as db_init_failed:
    logger.critical(
        "database_initialization_failed",
        error=str(db_init_failed),
        exc_info=True
    )

    raise DatabaseSessionError(
        "Database service is temprarily unavailable."
    ) from db_init_failed

Base = declarative_base()