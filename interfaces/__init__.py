#!/usr/bin/env python3
"""
Interfaces Package
==================

Provides interface definitions for the game system including:
- Game controller interfaces (Task #4)
- Observer pattern interfaces (Task #5)
"""

# Game interfaces (Task #4)
from .game_interfaces import *

# Observer pattern interfaces (Task #5)  
from .observer_interfaces import (
    GameEventType, GameEvent, Observer, Subject,
    AbstractObserver, AbstractSubject, EventManagerProtocol,
    HooksEventManager, event_manager, EventFilter
)

# UI Observer implementation
from .ui_observer import UIObserver, GameEventPublisher

__all__ = [
    # Game interfaces
    'UIServiceProtocol', 'GameServiceProtocol', 'CombatControllerInterface',
    'CharacterControllerInterface', 'InventoryControllerInterface', 'ComboControllerInterface',
    'DemoEventHandlerInterface', 'DisplayManagerInterface', 'GameStateManagerInterface',
    'SuccessResult', 'ErrorResult', 'ResultUnion',
    
    # Observer pattern
    'GameEventType', 'GameEvent', 'Observer', 'Subject',
    'AbstractObserver', 'AbstractSubject', 'EventManagerProtocol',
    'HooksEventManager', 'event_manager', 'EventFilter',
    'UIObserver', 'GameEventPublisher'
]
