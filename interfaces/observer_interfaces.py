#!/usr/bin/env python3
"""
Observer Pattern Bridge
=======================

Provides a bridge/adapter between the existing hooks system and observer pattern interfaces.
This implements Task #5 from the refactoring roadmap by leveraging the existing event bus.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Union
from enum import Enum

# Import existing hooks system
from game_sys.hooks.hooks_setup import (
    emit, on, off, once, on_pre, on_post, 
    emit_async, emit_with_hooks, emit_with_hooks_async,
    # Import existing event constants
    ON_ATTACK_HIT, ON_DEATH, ON_LEVEL_UP, ON_EXPERIENCE_GAINED,
    ON_HEALTH_CHANGED, ON_MANA_CHANGED, ON_STAMINA_CHANGED,
    ON_EQUIP_ITEM, ON_UNEQUIP_ITEM, ON_ITEM_ACQUIRED, ON_ITEM_LOST,
    ON_SPELL_CAST, ON_ENCHANTMENT_APPLIED, ON_COMBAT_START, ON_COMBAT_END,
    ON_SKILL_LEARNED, ON_CHARACTER_CREATED
)


class GameEventType(Enum):
    """Types of game events that can be observed."""
    
    # Character Events
    PLAYER_STAT_CHANGED = "player_stat_changed"
    PLAYER_LEVEL_UP = "player_level_up"
    PLAYER_HEALTH_CHANGED = "player_health_changed"
    PLAYER_MANA_CHANGED = "player_mana_changed"
    PLAYER_STAMINA_CHANGED = "player_stamina_changed"
    PLAYER_XP_GAINED = "player_xp_gained"
    
    # Character Creation Events
    CHARACTER_CREATED = "character_created"
    CHARACTER_FINALIZED = "character_finalized"
    CHARACTER_SAVED = "character_saved"
    CHARACTER_LOADED = "character_loaded"
    TEMPLATE_SELECTED = "template_selected"
    STATS_ALLOCATED = "stats_allocated"
    CHARACTER_RESET = "character_reset"
    
    # Combat Events
    COMBAT_STARTED = "combat_started"
    COMBAT_ENDED = "combat_ended"
    ATTACK_PERFORMED = "attack_performed"
    DAMAGE_DEALT = "damage_dealt"
    SPELL_CAST = "spell_cast"
    SKILL_USED = "skill_used"
    
    # Inventory Events
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_EQUIPPED = "item_equipped"
    ITEM_UNEQUIPPED = "item_unequipped"
    INVENTORY_CHANGED = "inventory_changed"
    
    # Progression Events
    SKILL_LEARNED = "skill_learned"
    SPELL_LEARNED = "spell_learned"
    ENCHANTMENT_LEARNED = "enchantment_learned"
    
    # UI Events
    TAB_CHANGED = "tab_changed"
    DISPLAY_UPDATE_REQUESTED = "display_update_requested"
    
    # System Events
    GAME_STATE_CHANGED = "game_state_changed"
    ERROR_OCCURRED = "error_occurred"


class GameEvent:
    """Represents a game event with data."""
    
    def __init__(self, event_type: GameEventType, data: Optional[Dict[str, Any]] = None, source: Optional[Any] = None):
        self.event_type = event_type
        self.data = data or {}
        self.source = source
        self.timestamp = None  # Could add timestamp if needed
    
    def __repr__(self) -> str:
        return f"GameEvent(type={self.event_type.value}, data={self.data})"


class Observer(Protocol):
    """Protocol for objects that can observe game events."""
    
    def notify(self, event: GameEvent) -> None:
        """Handle a game event notification."""
        ...


class Subject(Protocol):
    """Protocol for objects that can be observed."""
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer to this subject."""
        ...
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer from this subject."""
        ...
    
    def notify_observers(self, event: GameEvent) -> None:
        """Notify all attached observers of an event."""
        ...


class AbstractObserver(ABC):
    """Abstract base class for observers."""
    
    @abstractmethod
    def notify(self, event: GameEvent) -> None:
        """Handle a game event notification."""
        pass


class AbstractSubject(ABC):
    """Abstract base class for subjects."""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer to this subject."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer from this subject."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: GameEvent) -> None:
        """Notify all attached observers of an event."""
        for observer in self._observers:
            try:
                observer.notify(event)
            except Exception as e:
                # Log error but don't break the observer chain
                print(f"Observer notification error: {e}")


class EventManagerProtocol(Protocol):
    """Protocol for centralized event management."""
    
    def subscribe(self, event_type: GameEventType, observer: Observer) -> None:
        """Subscribe an observer to a specific event type."""
        ...
    
    def unsubscribe(self, event_type: GameEventType, observer: Observer) -> None:
        """Unsubscribe an observer from a specific event type."""
        ...
    
    def publish(self, event: GameEvent) -> None:
        """Publish an event to all subscribed observers."""
        ...
    
    def clear_subscribers(self, event_type: Optional[GameEventType] = None) -> None:
        """Clear all subscribers for an event type, or all subscribers if None."""
        ...


class HooksEventManager:
    """
    Event Manager that bridges Observer pattern with existing hooks system.
    
    This class allows components to use observer pattern while leveraging
    the existing event bus infrastructure.
    """
    
    def __init__(self):
        self._observers: Dict[GameEventType, List[Observer]] = {}
        self._hook_listeners: Dict[GameEventType, Any] = {}
        self._event_mapping = self._create_event_mapping()
    
    def _create_event_mapping(self) -> Dict[GameEventType, str]:
        """Map GameEventType to existing hook event names."""
        return {
            # Character Events -> Hook Events
            GameEventType.PLAYER_LEVEL_UP: ON_LEVEL_UP,
            GameEventType.PLAYER_HEALTH_CHANGED: ON_HEALTH_CHANGED,
            GameEventType.PLAYER_MANA_CHANGED: ON_MANA_CHANGED,
            GameEventType.PLAYER_STAMINA_CHANGED: ON_STAMINA_CHANGED,
            GameEventType.PLAYER_XP_GAINED: ON_EXPERIENCE_GAINED,
            
            # Combat Events -> Hook Events
            GameEventType.COMBAT_STARTED: ON_COMBAT_START,
            GameEventType.COMBAT_ENDED: ON_COMBAT_END,
            GameEventType.ATTACK_PERFORMED: ON_ATTACK_HIT,
            GameEventType.SPELL_CAST: ON_SPELL_CAST,
            
            # Inventory Events -> Hook Events
            GameEventType.ITEM_EQUIPPED: ON_EQUIP_ITEM,
            GameEventType.ITEM_UNEQUIPPED: ON_UNEQUIP_ITEM,
            GameEventType.ITEM_ADDED: ON_ITEM_ACQUIRED,
            GameEventType.ITEM_REMOVED: ON_ITEM_LOST,
            
            # Progression Events -> Hook Events
            GameEventType.SKILL_LEARNED: ON_SKILL_LEARNED,
            
            # System Events -> Hook Events
            GameEventType.ENCHANTMENT_LEARNED: ON_ENCHANTMENT_APPLIED,
        }
    
    def subscribe(self, event_type: GameEventType, observer: Observer) -> None:
        """Subscribe an observer to a specific event type."""
        if event_type not in self._observers:
            self._observers[event_type] = []
            
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)
            
            # Set up hook listener if this is the first observer for this event
            if len(self._observers[event_type]) == 1:
                self._register_hook_listener(event_type)
    
    def unsubscribe(self, event_type: GameEventType, observer: Observer) -> None:
        """Unsubscribe an observer from a specific event type."""
        if event_type in self._observers and observer in self._observers[event_type]:
            self._observers[event_type].remove(observer)
            
            # Remove hook listener if no more observers for this event
            if len(self._observers[event_type]) == 0:
                self._unregister_hook_listener(event_type)
    
    def publish(self, event: GameEvent) -> None:
        """Publish an event to all subscribed observers."""
        # Notify direct observers
        if event.event_type in self._observers:
            for observer in self._observers[event.event_type]:
                try:
                    observer.notify(event)
                except Exception as e:
                    print(f"Observer notification error: {e}")
        
        # Also emit to hook system for compatibility
        hook_event = self._event_mapping.get(event.event_type)
        if hook_event:
            emit(hook_event, event.data)
    
    def _register_hook_listener(self, event_type: GameEventType) -> None:
        """Register a hook listener that forwards to observers."""
        hook_event = self._event_mapping.get(event_type)
        if hook_event and event_type not in self._hook_listeners:
            def listener(*args, **kwargs):
                # Convert hook call to GameEvent
                data = kwargs if kwargs else {}
                if args:
                    data['args'] = args
                event = GameEvent(event_type, data)
                
                # Notify observers
                for observer in self._observers.get(event_type, []):
                    try:
                        observer.notify(event)
                    except Exception as e:
                        print(f"Observer notification error: {e}")
            
            on(hook_event, listener)
            self._hook_listeners[event_type] = listener
    
    def _unregister_hook_listener(self, event_type: GameEventType) -> None:
        """Unregister a hook listener."""
        hook_event = self._event_mapping.get(event_type)
        if hook_event and event_type in self._hook_listeners:
            off(hook_event, self._hook_listeners[event_type])
            del self._hook_listeners[event_type]
    
    def clear_subscribers(self, event_type: Optional[GameEventType] = None) -> None:
        """Clear all subscribers for an event type, or all subscribers if None."""
        if event_type:
            if event_type in self._observers:
                self._observers[event_type].clear()
                self._unregister_hook_listener(event_type)
        else:
            for et in list(self._observers.keys()):
                self._observers[et].clear()
                self._unregister_hook_listener(et)
            self._observers.clear()


# Global event manager instance
event_manager = HooksEventManager()


class UIObserverProtocol(Protocol):
    """Protocol for UI components that observe game events."""
    
    def update_display(self, event_type: GameEventType, data: Dict[str, Any]) -> None:
        """Update the display based on the event."""
        ...
    
    def handle_error(self, error_message: str, error_type: str = "error") -> None:
        """Handle error events."""
        ...


class GameControllerObserverProtocol(Protocol):
    """Protocol for game controllers that both observe and emit events."""
    
    def handle_game_event(self, event: GameEvent) -> None:
        """Handle a game event as a controller."""
        ...
    
    def emit_event(self, event_type: GameEventType, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit a game event."""
        ...


# Type aliases for better readability
EventData = Dict[str, Any]
ObserverList = List[Observer]
EventSubscriptions = Dict[GameEventType, ObserverList]


class EventFilter:
    """Utility class for filtering events."""
    
    @staticmethod
    def is_character_event(event_type: GameEventType) -> bool:
        """Check if event is character-related."""
        character_events = {
            GameEventType.PLAYER_STAT_CHANGED,
            GameEventType.PLAYER_LEVEL_UP,
            GameEventType.PLAYER_HEALTH_CHANGED,
            GameEventType.PLAYER_MANA_CHANGED,
            GameEventType.PLAYER_STAMINA_CHANGED,
            GameEventType.PLAYER_XP_GAINED
        }
        return event_type in character_events
    
    @staticmethod
    def is_combat_event(event_type: GameEventType) -> bool:
        """Check if event is combat-related."""
        combat_events = {
            GameEventType.COMBAT_STARTED,
            GameEventType.COMBAT_ENDED,
            GameEventType.ATTACK_PERFORMED,
            GameEventType.DAMAGE_DEALT,
            GameEventType.SPELL_CAST,
            GameEventType.SKILL_USED
        }
        return event_type in combat_events
    
    @staticmethod
    def is_inventory_event(event_type: GameEventType) -> bool:
        """Check if event is inventory-related."""
        inventory_events = {
            GameEventType.ITEM_ADDED,
            GameEventType.ITEM_REMOVED,
            GameEventType.ITEM_EQUIPPED,
            GameEventType.ITEM_UNEQUIPPED,
            GameEventType.INVENTORY_CHANGED
        }
        return event_type in inventory_events
    
    @staticmethod
    def requires_ui_update(event_type: GameEventType) -> bool:
        """Check if event requires UI update."""
        ui_update_events = {
            GameEventType.PLAYER_STAT_CHANGED,
            GameEventType.PLAYER_LEVEL_UP,
            GameEventType.PLAYER_HEALTH_CHANGED,
            GameEventType.PLAYER_MANA_CHANGED,
            GameEventType.PLAYER_STAMINA_CHANGED,
            GameEventType.INVENTORY_CHANGED,
            GameEventType.ITEM_EQUIPPED,
            GameEventType.ITEM_UNEQUIPPED,
            GameEventType.COMBAT_ENDED,
            GameEventType.SKILL_LEARNED,
            GameEventType.SPELL_LEARNED,
            GameEventType.ENCHANTMENT_LEARNED
        }
        return event_type in ui_update_events
