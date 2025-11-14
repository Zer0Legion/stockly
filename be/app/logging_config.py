import logging
import os
from typing import Optional


def configure_logging(level: int = logging.INFO, file_path: Optional[str] = None) -> None:
    """Configure application logging in one place.

    - Sets a basic formatter/handler for the root logger.
    - Adjusts uvicorn loggers to avoid duplicate output.
    - Call this once at application startup (e.g. in `main.py`).
    """
    # basicConfig with force=True replaces existing handlers (Python 3.8+)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Remove existing handlers to avoid duplicates
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    root.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # File handler (default temp.log) if requested or if env LOG_TO_FILE is true
    if file_path is None:
        if os.environ.get("LOG_FILE"):
            file_path = os.environ.get("LOG_FILE")
        elif os.environ.get("LOG_TO_FILE", "false").lower() in ("1", "true", "yes"):
            file_path = "temp.log"
        else:
            file_path = "temp.log"  # per request always log to temp.log

    if file_path is not None:
        try:
            fh = logging.FileHandler(file_path, mode="a", encoding="utf-8")
            fh.setFormatter(formatter)
            root.addHandler(fh)
        except OSError:
            # If file cannot be opened, keep console logging only.
            pass

    # Keep uvicorn logs visible but prevent propagation duplicates
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").propagate = False
    logging.getLogger("uvicorn.access").propagate = False


def get_logger(name: Optional[str] = "stockly") -> logging.Logger:
    """Return a named logger for the application.

    Use `get_logger()` in modules to obtain the shared logger configured by
    `configure_logging()`.
    """
    return logging.getLogger(name)
