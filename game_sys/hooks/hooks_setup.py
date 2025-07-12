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
ON_PRELEVEL_UP = 'pre_level_up'
ON_POSTLEVEL_UP = 'post_level_up'
ON_EXPERIENCE_GAINED = 'experience_gained'
ON_HEALTH_CHANGED = 'health_changed'
ON_MANA_CHANGED = 'mana_changed'
ON_STAMINA_CHANGED = 'stamina_changed'
ON_STATUS_CHANGED = 'status_changed'
ON_EQUIP_ITEM = 'equip_item'
ON_UNEQUIP_ITEM = 'unequip_item'
ON_ITEM_ACQUIRED = 'item_acquired'
ON_ITEM_LOST = 'item_lost'
ON_ABILITY_LEARNED = 'ability_learned'
ON_ABILITY_UPGRADED = 'ability_upgraded'
ON_SPELL_CAST = 'spell_cast'
ON_SPELL_HIT = 'spell_hit'
ON_SPELL_MISSED = 'spell_missed'
ON_SPELL_FAILED = 'spell_failed'
ON_ENCHANTMENT_APPLIED = 'enchantment_applied'
ON_ENCHANTMENT_REMOVED = 'enchantment_removed'
ON_ENCHANTMENT_EXPIRED = 'enchantment_expired'
ON_CRITICAL_HIT = 'critical_hit'
ON_DODGE = 'dodge'
ON_BLOCK = 'block'
ON_PARRY = 'parry'
ON_DAMAGE_TAKEN = 'damage_taken'
ON_DAMAGE_DEALT = 'damage_dealt'
ON_HEALING_RECEIVED = 'healing_received'
ON_HEALING_DONE = 'healing_done'
ON_COMBAT_START = 'combat_start'
ON_COMBAT_END = 'combat_end'
ON_TURN_START = 'turn_start'
ON_TURN_END = 'turn_end'
ON_ROUND_START = 'round_start'
ON_ROUND_END = 'round_end'
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
ON_DESPAWN = 'despawn'
ON_LEVEL_START = 'level_start'
ON_LEVEL_COMPLETE = 'level_complete'
ON_LEVEL_FAIL = 'level_fail'
ON_QUEST_STARTED = 'quest_started'
ON_QUEST_COMPLETED = 'quest_completed'
ON_QUEST_FAILED = 'quest_failed'
ON_ACHIEVEMENT_UNLOCKED = 'achievement_unlocked'
ON_FAST_TRAVEL = 'fast_travel'
ON_CRAFTING_STARTED = 'crafting_started'
ON_CRAFTING_COMPLETED = 'crafting_completed'
ON_CRAFTING_FAILED = 'crafting_failed'
ON_RECIPE_LEARNED = 'recipe_learned'
ON_RECIPE_FORGOTTEN = 'recipe_forgotten'
ON_LOOT_ACQUIRED = 'loot_acquired'
ON_LOOT_DROPPED = 'loot_dropped'
ON_SAVE_GAME = 'save_game'
ON_LOAD_GAME = 'load_game'
ON_GAME_START = 'game_start'
ON_GAME_EXIT = 'game_exit'
ON_PAUSE = 'pause'
ON_UNPAUSE = 'unpause'
# Initialize the hooks system

hooks_logger.info("Hooks system initialized")
