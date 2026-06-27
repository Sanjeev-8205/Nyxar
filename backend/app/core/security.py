import secrets
from fastapi import Header, HTTPException
from app.core.settings import get_settings
import structlog

logger=structlog.get_logger()

async def verify_api_key(
        x_api_key:str = Header(default=None)
):
    
    settings=get_settings()

    if x_api_key is None:
        logger.error("Missing_API_key")
        raise HTTPException(status_code=401, detail="Missing API key")

    if not secrets.compare_digest(x_api_key, settings.PROTECT_API_KEY):
        logger.error("Wrong_API_key")
        raise HTTPException(status_code=401, detail="Unauthorized Access")
    
    return True