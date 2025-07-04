# game_sys/combat/combat.py
"""
Combat system compatibility module.

This module provides the CombatCapabilities class that tests expect,
serving as the main entry point for the combat system.
"""

# Re-export the main classes for compatibility
from .capabilities import CombatCapabilities
from .engine import CombatEngine
from .events import CombatEvent, CombatOutcome

__all__ = [
    'CombatCapabilities', 'CombatEngine', 'CombatEvent', 'CombatOutcome'
]
