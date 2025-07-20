#!/usr/bin/env python3
"""
UI Observer Implementation
==========================

Concrete observer implementation for UI updates that bridges with the existing hooks system.
"""

from typing import Dict, Any, Optional, Set
from .observer_interfaces import (
    Observer, GameEvent, GameEventType, EventFilter,
    AbstractObserver, event_manager
)


class UIObserver(AbstractObserver):
    """
    Observer that handles UI updates in response to game events.
    Designed to work with the existing demo UI system.
    """
    
    def __init__(self, ui_service=None):
        """
        Initialize the UI observer.
        
        Args:
            ui_service: The UI service object (e.g., DemoUI instance)
        """
        self.ui_service = ui_service
        self._subscribed_events: Set[GameEventType] = set()
        
        # Default event subscriptions for common UI updates
        self._subscribe_to_ui_events()
    
    def _subscribe_to_ui_events(self) -> None:
        """Subscribe to events that require UI updates."""
        ui_events = [
            GameEventType.PLAYER_STAT_CHANGED,
            GameEventType.PLAYER_LEVEL_UP,
            GameEventType.PLAYER_HEALTH_CHANGED,
            GameEventType.PLAYER_MANA_CHANGED,
            GameEventType.PLAYER_STAMINA_CHANGED,
            GameEventType.PLAYER_XP_GAINED,
            GameEventType.INVENTORY_CHANGED,
            GameEventType.ITEM_EQUIPPED,
            GameEventType.ITEM_UNEQUIPPED,
            GameEventType.COMBAT_ENDED,
            GameEventType.SKILL_LEARNED,
            GameEventType.SPELL_LEARNED,
            GameEventType.ENCHANTMENT_LEARNED,
            GameEventType.DISPLAY_UPDATE_REQUESTED
        ]
        
        for event_type in ui_events:
            self.subscribe(event_type)
    
    def subscribe(self, event_type: GameEventType) -> None:
        """Subscribe to a specific event type."""
        if event_type not in self._subscribed_events:
            event_manager.subscribe(event_type, self)
            self._subscribed_events.add(event_type)
    
    def unsubscribe(self, event_type: GameEventType) -> None:
        """Unsubscribe from a specific event type."""
        if event_type in self._subscribed_events:
            event_manager.unsubscribe(event_type, self)
            self._subscribed_events.remove(event_type)
    
    def set_ui_service(self, ui_service) -> None:
        """Set or update the UI service."""
        self.ui_service = ui_service
    
    def notify(self, event: GameEvent) -> None:
        """Handle game event notifications."""
        try:
            self._handle_event(event)
        except Exception as e:
            print(f"UIObserver error handling event {event.event_type}: {e}")
    
    def _handle_event(self, event: GameEvent) -> None:
        """Handle specific event types."""
        event_type = event.event_type
        data = event.data
        
        # Character Events
        if EventFilter.is_character_event(event_type):
            self._handle_character_event(event_type, data)
        
        # Inventory Events
        elif EventFilter.is_inventory_event(event_type):
            self._handle_inventory_event(event_type, data)
        
        # Combat Events
        elif EventFilter.is_combat_event(event_type):
            self._handle_combat_event(event_type, data)
        
        # Progression Events
        elif event_type in [GameEventType.SKILL_LEARNED, GameEventType.SPELL_LEARNED, GameEventType.ENCHANTMENT_LEARNED]:
            self._handle_progression_event(event_type, data)
        
        # UI Events
        elif event_type == GameEventType.DISPLAY_UPDATE_REQUESTED:
            self._handle_display_update(data)
        
        # Error Events
        elif event_type == GameEventType.ERROR_OCCURRED:
            self._handle_error_event(data)
    
    def _handle_character_event(self, event_type: GameEventType, data: Dict[str, Any]) -> None:
        """Handle character-related events."""
        if not self.ui_service:
            return
            
        if hasattr(self.ui_service, 'update_character_display'):
            self.ui_service.update_character_display()
        
        if event_type == GameEventType.PLAYER_LEVEL_UP:
            if hasattr(self.ui_service, 'update_leveling_display'):
                self.ui_service.update_leveling_display()
                
            if hasattr(self.ui_service, 'log_message'):
                level = data.get('level', 'Unknown')
                self.ui_service.log_message(f"🎉 Level Up! You are now level {level}!", "info")
    
    def _handle_inventory_event(self, event_type: GameEventType, data: Dict[str, Any]) -> None:
        """Handle inventory-related events."""
        if not self.ui_service:
            return
            
        if hasattr(self.ui_service, 'update_inventory_display'):
            self.ui_service.update_inventory_display()
            
        if hasattr(self.ui_service, 'update_equipment_display'):
            self.ui_service.update_equipment_display()
        
        # Log specific inventory actions
        if hasattr(self.ui_service, 'log_message'):
            if event_type == GameEventType.ITEM_EQUIPPED:
                item_name = data.get('item_name', 'Unknown Item')
                self.ui_service.log_message(f"⚔️ Equipped: {item_name}", "info")
            elif event_type == GameEventType.ITEM_UNEQUIPPED:
                item_name = data.get('item_name', 'Unknown Item')
                self.ui_service.log_message(f"📦 Unequipped: {item_name}", "info")
    
    def _handle_combat_event(self, event_type: GameEventType, data: Dict[str, Any]) -> None:
        """Handle combat-related events."""
        if not self.ui_service:
            return
            
        if event_type == GameEventType.COMBAT_ENDED:
            # Update all relevant displays after combat
            if hasattr(self.ui_service, 'update_character_display'):
                self.ui_service.update_character_display()
            if hasattr(self.ui_service, 'update_inventory_display'):
                self.ui_service.update_inventory_display()
                
            if hasattr(self.ui_service, 'log_message'):
                result = data.get('result', 'finished')
                self.ui_service.log_message(f"⚔️ Combat {result}", "info")
    
    def _handle_progression_event(self, event_type: GameEventType, data: Dict[str, Any]) -> None:
        """Handle progression-related events (skills, spells, enchantments)."""
        if not self.ui_service:
            return
            
        if hasattr(self.ui_service, 'update_progression_display'):
            self.ui_service.update_progression_display()
        
        if hasattr(self.ui_service, 'log_message'):
            if event_type == GameEventType.SKILL_LEARNED:
                skill_name = data.get('skill_name', 'Unknown Skill')
                self.ui_service.log_message(f"💪 Learned Skill: {skill_name}", "info")
            elif event_type == GameEventType.SPELL_LEARNED:
                spell_name = data.get('spell_name', 'Unknown Spell')
                self.ui_service.log_message(f"✨ Learned Spell: {spell_name}", "info")
            elif event_type == GameEventType.ENCHANTMENT_LEARNED:
                enchant_name = data.get('enchant_name', 'Unknown Enchantment')
                self.ui_service.log_message(f"🔮 Learned Enchantment: {enchant_name}", "info")
    
    def _handle_display_update(self, data: Dict[str, Any]) -> None:
        """Handle display update requests."""
        if not self.ui_service:
            return
            
        update_type = data.get('update_type', 'all')
        
        if update_type == 'all' or update_type == 'character':
            if hasattr(self.ui_service, 'update_character_display'):
                self.ui_service.update_character_display()
        
        if update_type == 'all' or update_type == 'inventory':
            if hasattr(self.ui_service, 'update_inventory_display'):
                self.ui_service.update_inventory_display()
                
        if update_type == 'all' or update_type == 'equipment':
            if hasattr(self.ui_service, 'update_equipment_display'):
                self.ui_service.update_equipment_display()
                
        if update_type == 'all' or update_type == 'progression':
            if hasattr(self.ui_service, 'update_progression_display'):
                self.ui_service.update_progression_display()
    
    def _handle_error_event(self, data: Dict[str, Any]) -> None:
        """Handle error events."""
        if not self.ui_service:
            return
            
        if hasattr(self.ui_service, 'log_message'):
            error_msg = data.get('message', 'Unknown error occurred')
            error_type = data.get('type', 'error')
            self.ui_service.log_message(f"❌ Error: {error_msg}", error_type)
    
    def cleanup(self) -> None:
        """Clean up subscriptions when observer is no longer needed."""
        for event_type in list(self._subscribed_events):
            self.unsubscribe(event_type)


class GameEventPublisher:
    """
    Utility class for publishing game events.
    Can be used by controllers or demo.py to emit events.
    """
    
    @staticmethod
    def publish_stat_change(stat_name: str, old_value: Any, new_value: Any, source=None) -> None:
        """Publish a player stat change event."""
        event = GameEvent(
            GameEventType.PLAYER_STAT_CHANGED,
            {
                'stat_name': stat_name,
                'old_value': old_value,
                'new_value': new_value
            },
            source
        )
        event_manager.publish(event)
    
    @staticmethod
    def publish_level_up(new_level: int, source=None) -> None:
        """Publish a level up event."""
        event = GameEvent(
            GameEventType.PLAYER_LEVEL_UP,
            {'level': new_level},
            source
        )
        event_manager.publish(event)
    
    @staticmethod
    def publish_skill_learned(skill_name: str, source=None) -> None:
        """Publish a skill learned event."""
        event = GameEvent(
            GameEventType.SKILL_LEARNED,
            {'skill_name': skill_name},
            source
        )
        event_manager.publish(event)
    
    @staticmethod
    def publish_spell_learned(spell_name: str, source=None) -> None:
        """Publish a spell learned event."""
        event = GameEvent(
            GameEventType.SPELL_LEARNED,
            {'spell_name': spell_name},
            source
        )
        event_manager.publish(event)
    
    @staticmethod
    def publish_enchantment_learned(enchant_name: str, source=None) -> None:
        """Publish an enchantment learned event."""
        event = GameEvent(
            GameEventType.ENCHANTMENT_LEARNED,
            {'enchant_name': enchant_name},
            source
        )
        event_manager.publish(event)
    
    @staticmethod
    def publish_inventory_change(action: str, item_name: str = None, source=None) -> None:
        """Publish an inventory change event."""
        event = GameEvent(
            GameEventType.INVENTORY_CHANGED,
            {
                'action': action,
                'item_name': item_name
            },
            source
        )
        event_manager.publish(event)
    
    @staticmethod
    def publish_display_update_request(update_type: str = 'all', source=None) -> None:
        """Request a display update."""
        event = GameEvent(
            GameEventType.DISPLAY_UPDATE_REQUESTED,
            {'update_type': update_type},
            source
        )
        event_manager.publish(event)
    
    @staticmethod
    def publish_error(message: str, error_type: str = 'error', source=None) -> None:
        """Publish an error event."""
        event = GameEvent(
            GameEventType.ERROR_OCCURRED,
            {
                'message': message,
                'type': error_type
            },
            source
        )
        event_manager.publish(event)
