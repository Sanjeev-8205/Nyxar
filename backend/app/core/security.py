from fastapi import Header, HTTPException
from app.core.settings import get_settings

async def verify_api_key(
        x_api_key:str = Header(default=None)
):
    
    settings=get_settings()

    if x_api_key!=settings.PROTECT_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access")
    
    return True