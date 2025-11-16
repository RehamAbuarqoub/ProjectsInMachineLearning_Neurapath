import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# EXACT formatter requested by professor
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging(log_dir: Path | None = None) -> None:
    """
    Configure root and app loggers with:
    - Console (INFO)
    - Rotating file handler (INFO) at backend/app/logs/app.log
    """
    log_dir = log_dir or Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Clear old handlers (avoid duplicates on reload)
    for h in list(root.handlers):
        root.removeHandler(h)

    fmt = logging.Formatter(FORMAT)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # Rotating file handler (1MB, keep 3 backups)
    fh = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    root.addHandler(fh)
