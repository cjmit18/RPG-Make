"""
Event Bus - Strongly Typed Event System for RPG Engine
Supports async event handling with middleware and type safety
"""
import asyncio
from typing import Dict, List, Type, TypeVar, Generic, Protocol, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass(frozen=True)
class GameEvent(ABC):
    """Base class for all game events"""
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None

@dataclass(frozen=True)
class CharacterCreatedEvent(GameEvent):
    character_id: str = ""
    character_name: str = ""
    character_type: str = ""
    initial_stats: Dict[str, int] = field(default_factory=dict)

@dataclass(frozen=True)
class CombatActionEvent(GameEvent):
    actor_id: str = ""
    target_id: str = ""
    action_type: str = ""
    damage_dealt: int = 0
    effects_applied: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class UIUpdateEvent(GameEvent):
    component_id: str = ""
    update_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

class EventHandler(Protocol, Generic[T]):
    """Protocol for event handlers"""
    async def handle(self, event: T) -> None: ...

class EventMiddleware(Protocol):
    """Protocol for event middleware"""
    async def process(self, event: GameEvent) -> GameEvent: ...

class LoggingMiddleware:
    """Middleware that logs all events"""
    
    def __init__(self, log_level: int = logging.DEBUG):
        self.log_level = log_level
    
    async def process(self, event: GameEvent) -> GameEvent:
        logger.log(self.log_level, f"Event: {event.__class__.__name__} from {event.source}")
        return event

class ValidationMiddleware:
    """Middleware that validates events"""
    
    async def process(self, event: GameEvent) -> GameEvent:
        # Basic validation - can be extended
        if not hasattr(event, 'timestamp') or event.timestamp <= 0:
            raise ValueError(f"Invalid event timestamp: {event}")
        return event

class EventBus:
    """
    Async-first event bus with strong typing and middleware support
    """
    
    def __init__(self):
        self.handlers: Dict[Type[GameEvent], List[EventHandler]] = {}
        self.middleware: List[EventMiddleware] = []
        self.event_history: List[GameEvent] = []
        self.max_history: int = 1000
        self._lock = asyncio.Lock()
        self.stats = {
            'events_published': 0,
            'events_handled': 0,
            'errors': 0
        }
    
    def add_middleware(self, middleware: EventMiddleware) -> None:
        """Add middleware to the event processing pipeline"""
        logger.debug(f"Adding middleware: {middleware.__class__.__name__}")
        self.middleware.append(middleware)
    
    def subscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Subscribe to events of a specific type"""
        logger.debug(f"Subscribing to {event_type.__name__}")
        
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Unsubscribe from events"""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
                logger.debug(f"Unsubscribed from {event_type.__name__}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type.__name__}")
    
    async def publish(self, event: GameEvent) -> None:
        """Publish an event to all subscribers"""
        async with self._lock:
            self.stats['events_published'] += 1
            
            try:
                # Apply middleware
                processed_event = event
                for middleware in self.middleware:
                    processed_event = await middleware.process(processed_event)
                
                # Add to history
                self.event_history.append(processed_event)
                if len(self.event_history) > self.max_history:
                    self.event_history.pop(0)
                
                # Notify handlers
                event_type = type(processed_event)
                if event_type in self.handlers:
                    # Run all handlers concurrently
                    handler_tasks = [
                        self._safe_handle_event(handler, processed_event)
                        for handler in self.handlers[event_type]
                    ]
                    
                    if handler_tasks:
                        await asyncio.gather(*handler_tasks, return_exceptions=True)
                        self.stats['events_handled'] += len(handler_tasks)
                
                logger.debug(f"Published event: {event_type.__name__}")
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error publishing event {event.__class__.__name__}: {e}")
                raise
    
    async def _safe_handle_event(self, handler: EventHandler, event: GameEvent) -> None:
        """Safely handle an event, catching and logging exceptions"""
        try:
            await handler.handle(event)
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Error in event handler {handler.__class__.__name__}: {e}")
    
    def get_event_history(self, event_type: Optional[Type[GameEvent]] = None, 
                         limit: Optional[int] = None) -> List[GameEvent]:
        """Get event history, optionally filtered by type"""
        history = self.event_history
        
        if event_type:
            history = [e for e in history if isinstance(e, event_type)]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            **self.stats,
            'handlers_registered': sum(len(handlers) for handlers in self.handlers.values()),
            'middleware_count': len(self.middleware),
            'history_size': len(self.event_history)
        }
    
    def clear_history(self) -> None:
        """Clear event history"""
        self.event_history.clear()
        logger.info("Event history cleared")
    
    async def shutdown(self) -> None:
        """Shutdown the event bus"""
        logger.info("Shutting down event bus...")
        self.handlers.clear()
        self.middleware.clear()
        self.clear_history()
        logger.info("Event bus shut down")
