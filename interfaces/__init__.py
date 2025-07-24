#!/usr/bin/env python3
"""
Interface Definitions Package
============================

Protocol definitions and interface contracts for the RPG engine.

Interfaces:
- GameInterfaces: Core game system protocols
- UIServiceProtocol: UI service interface definitions
- ServiceProtocols: Business logic service interfaces
- DataProtocols: Data access and persistence interfaces

Features:
- Type safety through protocol definitions
- Clear API contracts
- Dependency injection support
- Mock-friendly interfaces for testing
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
