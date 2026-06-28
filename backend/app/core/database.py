from sqlalchemy.orm import declarative_base
import structlog, re

logger = structlog.get_logger()

Base = declarative_base()
engine = None
SessionLocal = None


def init_db():
    global engine, SessionLocal
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.settings import get_settings

    class DatabaseSessionError(Exception):
        pass

    try:
        settings = get_settings()
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
        db_url = re.sub(r'\?.*$', '', db_url)
        engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=300)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as db_init_failed:
        logger.critical(
            "database_initialization_failed",
            error=str(db_init_failed),
            exc_info=True
        )
        raise DatabaseSessionError(
            "Database service is temporarily unavailable."
        ) from db_init_failed