# --- Inventory events ---
ON_PRE_ADD_ITEM = 'pre_add_item'
ON_POST_ADD_ITEM = 'post_add_item'
ON_PRE_REMOVE_ITEM = 'pre_remove_item'
ON_POST_REMOVE_ITEM = 'post_remove_item'
# --- Loot events ---
ON_PRE_GENERATE_LOOT = 'pre_generate_loot'
ON_POST_GENERATE_LOOT = 'post_generate_loot'
ON_ITEM_DROP = 'item_drop'
# game_sys/hooks/hooks_setup.py
"""
Module: game_sys.hooks.hooks_setup

Exports global event dispatch functions and common event constants.
"""
from game_sys.hooks.event_bus import event_bus
from game_sys.logging import hooks_logger, log_exception


# --- Expanded API with async and hook support ---
def on(event, listener):
    hooks_logger.debug(f"Registering hook for '{event}'")
    return event_bus.on(event, listener)

def off(event, listener):
    hooks_logger.debug(f"Removing hook for '{event}'")
    return event_bus.off(event, listener)

def emit(event, *args, **kwargs):
    hooks_logger.debug(f"Emitting event '{event}'")
    return event_bus.emit(event, *args, **kwargs)

async def emit_async(event, *args, **kwargs):
    hooks_logger.debug(f"[async] Emitting event '{event}'")
    return await event_bus.emit_async(event, *args, **kwargs)

def once(event, listener):
    hooks_logger.debug(f"Registering one-time hook for '{event}'")
    return event_bus.once(event, listener)

def on_pre(event, listener):
    hooks_logger.debug(f"Registering pre-hook for '{event}'")
    return event_bus.on_pre(event, listener)

def on_post(event, listener):
    hooks_logger.debug(f"Registering post-hook for '{event}'")
    return event_bus.on_post(event, listener)

def emit_with_hooks(event, *args, **kwargs):
    hooks_logger.debug(f"Emitting event with hooks '{event}'")
    return event_bus.emit_with_hooks(event, *args, **kwargs)

async def emit_with_hooks_async(event, *args, **kwargs):
    hooks_logger.debug(f"[async] Emitting event with hooks '{event}'")
    return await event_bus.emit_with_hooks_async(event, *args, **kwargs)


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
# --- Async save/load events ---
ON_PRE_SAVE = 'pre_save'
ON_POST_SAVE = 'post_save'
ON_PRE_LOAD = 'pre_load'
ON_POST_LOAD = 'post_load'
# ---
ON_SKILL_LEARNED = 'skill_learned'
ON_SKILL_UPGRADED = 'skill_upgraded'
ON_COMBO_TRIGGERED = 'combo_triggered'
ON_COMBO_FINISHED = 'combo_finished'
ON_SPAWN = 'spawn'

hooks_logger.info("Hooks system initialized")
