# game_sys/hooks/hooks_setup.py
"""
Module: game_sys.hooks.hooks_setup

Exports global event dispatch functions and common event constants.
"""
from game_sys.hooks.event_bus import event_bus
from game_sys.logging import hooks_logger, log_exception

# Define wrapped functions with logging
def on_with_logging(event, listener):
    """Wrapper for event_bus.on with logging"""
    hooks_logger.debug(f"Registering hook for '{event}'")
    return event_bus.on(event, listener)

def off_with_logging(event, listener):
    """Wrapper for event_bus.off with logging"""
    hooks_logger.debug(f"Removing hook for '{event}'")
    return event_bus.off(event, listener)

def emit_with_logging(event, *args, **kwargs):
    """Wrapper for event_bus.emit with logging"""
    hooks_logger.debug(f"Emitting event '{event}'")
    return event_bus.emit(event, *args, **kwargs)

# Re-export API with logging wrappers
on = on_with_logging
off = off_with_logging
emit = emit_with_logging

# Common events
ON_ATTACK_HIT = 'attack_hit'
ON_DEATH = 'death'
ON_LEVEL_UP = 'level_up'
ON_STATUS_APPLIED = 'status_applied'
ON_STATUS_EXPIRED = 'status_expired'
ON_ITEM_USED = 'item_used'
ON_ABILITY_CAST = 'ability_cast'
ON_INTERACT = 'interact'
ON_CHARACTER_CREATED = 'character_created'
ON_DATA_LOADED = 'data_loaded'
ON_JOB_ASSIGNED = 'job_assigned'
ON_CONFIG_CHANGED = 'config_changed'
ON_SKILL_LEARNED = 'skill_learned'
ON_SKILL_UPGRADED = 'skill_upgraded'
ON_COMBO_TRIGGERED = 'combo_triggered'
ON_COMBO_FINISHED = 'combo_finished'
ON_SPAWN = 'spawn'

hooks_logger.info("Hooks system initialized")
