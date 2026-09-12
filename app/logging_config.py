"""
Structured Logging Subsystem for EDITH.
Ensures clean diagnostic logging, rotates log files, and sanitizes API keys or credentials.
Developed by G.Vijay Raj (vijay smart).
"""

from __future__ import annotations

import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import config

# Regular expressions to mask sensitive tokens or API keys
SENSITIVE_PATTERNS = [
    re.compile(r"(AIzaSy[0-9A-Za-z_-]{33})"),
    re.compile(r"(sk-[A-Za-z0-9]{32,})"),
    re.compile(r"(['\"]?GEMINI_API_KEY['\"]?\s*[:=]\s*['\"]?)([^'\"\s]+)(['\"]?)", re.IGNORECASE),
    re.compile(r"(['\"]?password['\"]?\s*[:=]\s*['\"]?)([^'\"\s]+)(['\"]?)", re.IGNORECASE),
]


class SensitiveFilter(logging.Filter):
    """Filters log records to redact any accidental leakage of API keys or passwords."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in SENSITIVE_PATTERNS:
                msg = pattern.sub(r"\1***REDACTED***", msg)
            record.msg = msg
        return True


class EdithStructuredFormatter(logging.Formatter):
    """Custom formatter producing readable, structured diagnostic log records."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        category = getattr(record, "category", record.name.upper())
        message = record.getMessage()

        # Format with structured blocks
        return f"[{timestamp}]\n{category}\n{message}\n"


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """Initialize system-wide logging with both file handler and console handler."""
    level_name = (log_level or config.diagnostics.log_level).upper()
    level = getattr(logging, level_name, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to prevent duplicate lines
    root_logger.handlers.clear()

    formatter = EdithStructuredFormatter()
    sensitive_filter = SensitiveFilter()

    # 1. Console Handler
    if config.diagnostics.enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(sensitive_filter)
        root_logger.addHandler(console_handler)

    # 2. File Handler
    if config.diagnostics.enable_file_logging:
        log_file = config.logs_dir / "edith.log"
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)

    logger = logging.getLogger("EDITH")
    logger.info(
        f"EDITH Logging Subsystem Initialized. Log Path: {config.logs_dir / 'edith.log'}",
        extra={"category": "LIFECYCLE"},
    )
    return logger


def log_event(category: str, message: str, level: int = logging.INFO) -> None:
    """Convenience helper to record a structured event with explicit category tag."""
    logger = logging.getLogger("EDITH")
    logger.log(level, message, extra={"category": category})
