# core/logging.py

import logging
import logging.config
import os
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console": {
            "format": "[{levelname:^8}] {name}:{lineno} | {message}",
            "style": "{",
        },
        "file": {
            "format": "{asctime} [{levelname:^8}] {name}:{lineno} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "file",
            "level": "DEBUG",
            "filename": str(LOG_DIR / "game.log"),
            "encoding": "utf-8",
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },

    "loggers": {
        # you can override levels for noisy third-party libs here, e.g.:
        "gen": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        }
    },
}


def setup_logging():
    """
    Call once at program start to configure logging for the entire project.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
