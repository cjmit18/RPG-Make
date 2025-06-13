# File: logs.py

import logging
import logging.config
import os
import json
from pathlib import Path
from typing import Optional


# ─── Configuration ────────────────────────────────────────

# Where log files go
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# You can override the console/root level via the LOG_LEVEL env var:
ENV_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ─── JSON Formatter ────────────────────────────────────────


class JsonFormatter(logging.Formatter):
    """
    Outputs each LogRecord as a single-line JSON object.
    """
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level":     record.levelname,
            "module":    record.name,
            "lineno":    record.lineno,
            "message":   record.getMessage(),
        }
        # Include any extra/contextual fields if you use them:
        if record.args:
            payload["args"] = record.args
        safe_args = [str(a) for a in record.args]
        payload["args"] = safe_args
        return json.dumps(payload)

# ─── Logging Configuration Dict ───────────────────────────────────────────


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console": {
            "format": "[%(levelname)8s] %(name)s:%(lineno)d | %(message)s",
        },
        "file": {
            "format": (
                "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d | "
                "%(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": JsonFormatter,
        },
    },

    "handlers": {
        # 1) Console output at ENV_LOG_LEVEL
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": ENV_LOG_LEVEL,
            "stream": "ext://sys.stdout",
        },
        # 2) Rotating text logfile at DEBUG
        "file_text": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "level": "DEBUG",
            "filename": str(LOG_DIR / "game.log"),
            "maxBytes": 1_048_576,
            "backupCount": 3,
            "encoding": "utf-8",
        },
        # 3) Rotating JSON logfile at DEBUG
        "file_json": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "level": "DEBUG",
            "filename": str(LOG_DIR / "game.json.log"),
            "maxBytes": 1_048_576,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },

    "root": {
        "handlers": ["console", "file_text", "file_json"],
        "level": ENV_LOG_LEVEL,
    },
}


def setup_logging():
    """
    Call once at program startup to configure all loggers.
    Honors LOG_LEVEL env var for console & root level.
    """
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Use this in your modules:
        logger = get_logger(__name__)
    """
    return logging.getLogger(name or __name__)

# ─── Runtime Log-Level Control ────────────────────────────────────────────


def set_log_level(logger_name: str, level: str):
    """
    Change a logger’s level at runtime.
        set_log_level("game_sys.core.actor", "DEBUG")
    """
    lvl = getattr(logging, level.upper(), None)
    if lvl is None:
        raise ValueError(f"Invalid log level: {level}")
    logging.getLogger(logger_name).setLevel(lvl)
