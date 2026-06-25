import structlog
import logging

def setup_logging():

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    )

    wrapper_class=structlog.stdlib.BoundLogger