"""Configure console and rotating file logging for the pipeline."""

import logging
from logging.handlers import RotatingFileHandler

from common.utils import BASE_DIR


LOG_DIR = BASE_DIR / "logs"
LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"


def setup_logging(level="INFO"):
    root = logging.getLogger()

    if root.handlers:
        return  # Logging is already configured.

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(
            LOG_DIR / "pipeline.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        ),
    ]

    for handler in handlers:
        handler.setFormatter(formatter)
        root.addHandler(handler)

    root.setLevel(level)