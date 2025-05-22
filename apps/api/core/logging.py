import logging
import sys
from typing import Any

import structlog
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from apps.api.core.config import settings

def configure_logging() -> None:
    """Configure structured logging with structlog."""
    # Remove existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    )

    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.WARNING)

def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)

class OpenTelemetryProcessor:
    """Structlog processor that adds OpenTelemetry trace context to log records."""

    def __init__(self) -> None:
        self.tracer = trace.get_tracer(__name__)

    def __call__(self, logger: structlog.BoundLogger, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        """Add trace context to the event dict."""
        current_span = trace.get_current_span()
        if current_span.is_recording():
            event_dict["trace_id"] = format(current_span.get_span_context().trace_id, "032x")
            event_dict["span_id"] = format(current_span.get_span_context().span_id, "016x")
        return event_dict

def log_exception(logger: structlog.BoundLogger, exc: Exception, level: str = "error") -> None:
    """Log an exception with trace context and status."""
    current_span = trace.get_current_span()
    if current_span.is_recording():
        current_span.set_status(Status(StatusCode.ERROR, str(exc)))
        current_span.record_exception(exc)

    log_method = getattr(logger, level)
    log_method(
        "exception_occurred",
        exc_type=exc.__class__.__name__,
        exc_msg=str(exc),
        exc_info=True,
    ) 