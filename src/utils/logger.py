"""
Shared logger for the application.

Writes to both the console (for development) and logs/app.log
(for postmortem debugging).
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import settings


_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)-22s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _configure_root_logger() -> None:
    """Set up handlers on the root logger. Idempotent."""

    global _configured
    if _configured:
        return

    log_dir: Path = settings.project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler (stdout)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    # Rotating file handler (max 1 MB per file, 3 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger with our shared configuration applied.

    Usage:
        from src.utils.logger import get_logger
        log = get_logger(__name__)
        log.info("something happened")
    """
    _configure_root_logger()
    return logging.getLogger(name)