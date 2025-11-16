# backend/app/logging_config.py

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Required formatter for the assignment
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def configure_logging() -> None:
    """
    Configure root logging with:
    - Formatter: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    - Console handler
    - Rotating file handler (logs/app.log)

    Safe to call multiple times (won't duplicate handlers).
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if function is called more than once
    has_console = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    has_file = any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers)

    # Console handler (prints to Docker logs / terminal)
    if not has_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler (writes to logs/app.log inside the container)
    if not has_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1_000_000,  # ~1 MB per file
            backupCount=3,       # keep 3 backups
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
