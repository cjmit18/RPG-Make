#!/usr/bin/env python3
"""
Game System Logging Integration
==============================

This module integrates the game's logging system with the game system components.
"""

from logs.logs import get_logger, setup_logging

# Set up logging when this module is imported
setup_logging()

# Create loggers for the main game system components
engine_logger = get_logger("game_sys.engine")
character_logger = get_logger("game_sys.character")
combat_logger = get_logger("game_sys.combat") 
items_logger = get_logger("game_sys.items")
effects_logger = get_logger("game_sys.effects")
inventory_logger = get_logger("game_sys.inventory")
config_logger = get_logger("game_sys.config")
hooks_logger = get_logger("game_sys.hooks")
magic_logger = get_logger("game_sys.magic")

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

def init_game_logging():
    """Initialize game system logging."""
    engine_logger.info("Initializing engine logging")
    character_logger.info("Initializing character logging")
    combat_logger.info("Initializing combat logging")
    items_logger.info("Initializing items logging")
    effects_logger.info("Initializing effects logging")
    inventory_logger.info("Initializing inventory logging")
    config_logger.info("Initializing config logging")
    hooks_logger.info("Initializing hooks logging")
    magic_logger.info("Initializing magic logging")
    magic_logger.info("Initializing magic logging")
