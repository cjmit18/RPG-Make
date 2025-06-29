# game_sys/hooks/hooks_setup.py
"""
Module: game_sys.hooks.hooks_setup

Exports global event dispatch functions and common event constants.
"""
from game_sys.hooks.event_bus import event_bus

# Re-export API
on = event_bus.on
off = event_bus.off
emit = event_bus.emit

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
