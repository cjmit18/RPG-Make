# game_sys/combat/__init__.py
"""
Combat system package.

This package encapsulates all combat-related functionality, including:
- Combat capabilities and stats calculation
- Combat engine for attack processing
- Turn management and action resolution
- Combat events and state management
"""

from .capabilities import CombatCapabilities
from .engine import CombatEngine
from .events import CombatEvent, CombatOutcome
from .turn_manager import turn_manager, TurnManager
from .test_utils import swing, setup_deterministic_combat, CombatTestScenario

__all__ = [
    'CombatCapabilities',
    'CombatEngine',
    'CombatEvent',
    'CombatOutcome',
    'turn_manager',
    'TurnManager',
    'swing',
    'setup_deterministic_combat',
    'CombatTestScenario'
]
