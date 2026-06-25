import uuid
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]

        with structlog.contextvars.bound_contextvars(
            request_id=request_id, method=request.method, path=request.url.path
        ):
            start_time = time.perf_counter()

            logger.info("Request Started")

            response = await call_next(request)

            duration_ms = round((time.perf_counter()-start_time)*1000, 2)

            logger.info(
                "request_finished", 
                status_code = response.status_code,
                duration_ms=duration_ms
            )

            return response