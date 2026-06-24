from fastapi import APIRouter
from fastapi.responses import Response

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.core.settings import get_settings

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

security = HTTPBasic()
def verify_metrics_auth(credentials: HTTPBasicCredentials = Depends(security)):
    settings=get_settings()
    correct_username = secrets.compare_digest(
        credentials.username, settings.PROMETHEUS_METRICS_USERNAME
    )

    correct_password = secrets.compare_digest(
        credentials.password, settings.PROMETHEUS_METRICS_PASSWORD
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"}
        )

@router.get("/prometheus_metrics")
def get_prometheus_metrics(credentials: HTTPBasicCredentials = Depends(verify_metrics_auth)):

    return Response(
        generate_latest(),
        media_type = CONTENT_TYPE_LATEST
    )