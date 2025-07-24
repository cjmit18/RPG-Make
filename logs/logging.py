#!/usr/bin/env python3
"""
UI Logging Integration
=====================

This module integrates the game's logging system with the UI components.
"""

from logs.logs import get_logger, setup_logging
import sys

# Set up logging when this module is imported
setup_logging()

# Create loggers for the UI components
ui_logger = get_logger("ui")
rendering_logger = get_logger("rendering")
animation_logger = get_logger("ui.animation")
theme_logger = get_logger("ui.theme")
layout_logger = get_logger("ui.layout")

# Game UI specific logger
game_ui_logger = get_logger("game_ui")

def log_exception(func):
    """Decorator to log exceptions that occur in a function."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = get_logger(func.__module__)
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper

def init_ui_logging():
    """Initialize UI logging."""
    ui_logger.info("Initializing UI logging")
    rendering_logger.info("Initializing rendering logging")
    animation_logger.info("Initializing animation logging")
    theme_logger.info("Initializing theme logging")
    layout_logger.info("Initializing layout logging")
    game_ui_logger.info("Initializing game UI logging")
