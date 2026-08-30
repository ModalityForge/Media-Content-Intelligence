"""Structured logging with structlog."""

import logging
import sys
from typing import Any

import structlog

from app.config import settings


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if settings.environment != "local" else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging to classes."""

    @property
    def logger(self) -> structlog.BoundLogger:
        return get_logger(self.__class__.__name__)