import logging
from typing import Optional


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application logging in one place.

    - Sets a basic formatter/handler for the root logger.
    - Adjusts uvicorn loggers to avoid duplicate output.
    - Call this once at application startup (e.g. in `main.py`).
    """
    # basicConfig with force=True replaces existing handlers (Python 3.8+)
    try:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            force=True,
        )
    except TypeError:
        # older Python versions do not support `force`
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

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
