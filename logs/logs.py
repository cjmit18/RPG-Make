# logging_config.py

import logging
import logging.config
from pathlib import Path
# Ensure log directory exists
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
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "level": "DEBUG",
            "filename": str(LOG_DIR / "game.log"),
            "encoding": "utf-8",
            "maxBytes": 1048576,  # 1MB
            "backupCount": 3,
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },

    "loggers": {
        "gen": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        }
    },
}


def setup_logging():
    """
    Call once at program start to configure logging.
    """
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name=None):
    """
    Use in other modules: from logging_config import get_logger
    """
    return logging.getLogger(name or __name__)
