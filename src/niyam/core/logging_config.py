import logging

import structlog
from structlog.typing import Processor


def configure_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """Configure structured logging for the whole application.

    Local development gets readable, coloured output. Production gets one JSON
    object per line, which log tools can parse and filter by field.
    """
    renderer: Processor = (
        structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelNamesMapping()[level]),
        cache_logger_on_first_use=True,
    )
