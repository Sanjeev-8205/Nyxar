from fastapi import Header, HTTPException
import os

NYXAR_API_KEY = os.getenv("PROTECT_API_KEY")
os.environ["PROTECT_API_KEY"] = "test-key"

async def verify_api_key(
        x_api_key:str = Header(default=None)
):
    if x_api_key!=NYXAR_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access")
    
    return True