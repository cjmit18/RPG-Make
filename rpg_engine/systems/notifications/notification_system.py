"""
Notification System - Event-driven user feedback

This system demonstrates another observer pattern implementation by
listening to various game events and providing user notifications
for important character system changes.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from rpg_engine.core.event_bus import EventBus, GameEvent, EventHandler

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACHIEVEMENT = "achievement"


@dataclass(frozen=True)
class NotificationEvent(GameEvent):
    """Event fired when a notification should be displayed"""
    message: str = ""
    notification_type: NotificationType = NotificationType.INFO
    duration: float = 3.0
    character_id: str = ""


@dataclass
class Notification:
    """Represents a single notification"""
    id: str
    message: str
    notification_type: NotificationType
    timestamp: float
    duration: float
    character_id: str = ""
    displayed: bool = False


class NotificationSystem(EventHandler):
    """
    Event-driven notification system that demonstrates observer pattern.
    
    This system listens to various game events and creates user-friendly
    notifications, showing how to implement UI-focused reactive systems.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.notifications: List[Notification] = []
        self.notification_counter = 0
        
        # Subscribe to events we want to create notifications for
        self._setup_event_subscriptions()
        
        logger.info("Notification system initialized")
    
    def _setup_event_subscriptions(self) -> None:
        """Subscribe to events - demonstrates observer pattern"""
        # Import here to avoid circular imports
        from rpg_engine.systems.character.character_system import CharacterCreatedEvent
        from rpg_engine.systems.character.progression_system import CharacterLevelUpEvent
        from rpg_engine.systems.achievements.achievement_system import AchievementUnlockedEvent
        
        # Character events
        self.event_bus.subscribe(CharacterCreatedEvent, self)
        self.event_bus.subscribe(CharacterLevelUpEvent, self)
        
        # Achievement events
        self.event_bus.subscribe(AchievementUnlockedEvent, self)
        
        logger.info("Notification system subscribed to game events")
    
    async def handle(self, event: GameEvent) -> None:
        """Main event handler for creating notifications"""
        try:
            # Import here to avoid circular imports
            from rpg_engine.systems.character.character_system import CharacterCreatedEvent
            from rpg_engine.systems.character.progression_system import CharacterLevelUpEvent
            from rpg_engine.systems.achievements.achievement_system import AchievementUnlockedEvent
            
            if isinstance(event, CharacterCreatedEvent):
                await self._handle_character_created(event)
            elif isinstance(event, CharacterLevelUpEvent):
                await self._handle_level_up(event)
            elif isinstance(event, AchievementUnlockedEvent):
                await self._handle_achievement_unlocked(event)
                
        except Exception as e:
            logger.error(f"Error handling notification event {event.__class__.__name__}: {e}")
    
    async def _handle_character_created(self, event) -> None:
        """Create notification for character creation"""
        character_id = getattr(event, 'character_id', '')
        character_name = getattr(event, 'character_name', 'Unknown')
        
        message = f"🎉 Character '{character_name}' created successfully!"
        
        await self._create_notification(
            message=message,
            notification_type=NotificationType.SUCCESS,
            duration=4.0,
            character_id=character_id
        )
    
    async def _handle_level_up(self, event) -> None:
        """Create notification for level up"""
        character_id = getattr(event, 'character_id', '')
        new_level = getattr(event, 'new_level', 1)
        
        message = f"🆙 Level Up! You are now level {new_level}!"
        
        await self._create_notification(
            message=message,
            notification_type=NotificationType.SUCCESS,
            duration=5.0,
            character_id=character_id
        )
    
    async def _handle_achievement_unlocked(self, event) -> None:
        """Create notification for achievement unlock"""
        achievement_name = getattr(event, 'achievement_name', 'Unknown Achievement')
        achievement_description = getattr(event, 'achievement_description', '')
        points_awarded = getattr(event, 'points_awarded', 0)
        character_id = getattr(event, 'character_id', '')
        
        message = f"🏆 Achievement Unlocked: {achievement_name}!"
        if achievement_description:
            message += f" - {achievement_description}"
        if points_awarded > 0:
            message += f" (+{points_awarded} points)"
        
        await self._create_notification(
            message=message,
            notification_type=NotificationType.ACHIEVEMENT,
            duration=6.0,
            character_id=character_id
        )
    
    async def _create_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO, 
                                 duration: float = 3.0, character_id: str = "") -> None:
        """Create and store a notification, then fire a notification event"""
        self.notification_counter += 1
        notification_id = f"notification_{self.notification_counter}_{int(time.time())}"
        
        notification = Notification(
            id=notification_id,
            message=message,
            notification_type=notification_type,
            timestamp=time.time(),
            duration=duration,
            character_id=character_id
        )
        
        self.notifications.append(notification)
        
        # Fire notification event for UI systems to handle
        notification_event = NotificationEvent(
            message=message,
            notification_type=notification_type,
            duration=duration,
            character_id=character_id,
            timestamp=time.time()
        )
        
        await self.event_bus.publish(notification_event)
        
        # Log the notification
        logger.info(f"📢 Notification: {message}")
        
        # Clean up old notifications
        await self._cleanup_old_notifications()
    
    async def _cleanup_old_notifications(self) -> None:
        """Remove notifications older than their duration + 60 seconds"""
        current_time = time.time()
        cutoff_buffer = 60  # Keep notifications for 60 seconds after they should have expired
        
        self.notifications = [
            notification for notification in self.notifications
            if current_time - notification.timestamp < notification.duration + cutoff_buffer
        ]
    
    def get_recent_notifications(self, limit: int = 10) -> List[Notification]:
        """Get the most recent notifications"""
        # Sort by timestamp descending (newest first)
        sorted_notifications = sorted(self.notifications, key=lambda n: n.timestamp, reverse=True)
        return sorted_notifications[:limit]
    
    def get_notifications_for_character(self, character_id: str, limit: int = 10) -> List[Notification]:
        """Get notifications for a specific character"""
        character_notifications = [
            notification for notification in self.notifications
            if notification.character_id == character_id
        ]
        
        # Sort by timestamp descending (newest first) 
        sorted_notifications = sorted(character_notifications, key=lambda n: n.timestamp, reverse=True)
        return sorted_notifications[:limit]
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification system statistics"""
        type_counts = {}
        for notification in self.notifications:
            type_name = notification.notification_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'total_notifications': len(self.notifications),
            'notifications_by_type': type_counts,
            'oldest_notification_age': (time.time() - min(n.timestamp for n in self.notifications)) if self.notifications else 0,
            'newest_notification_age': (time.time() - max(n.timestamp for n in self.notifications)) if self.notifications else 0
        }
    
    async def clear_notifications(self) -> None:
        """Clear all notifications (for testing)"""
        self.notifications.clear()
        self.notification_counter = 0
        logger.info("All notifications cleared")


# Export for easier importing
__all__ = ['NotificationSystem', 'Notification', 'NotificationEvent', 'NotificationType']
