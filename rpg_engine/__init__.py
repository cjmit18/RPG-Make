# New RPG Engine - Async First Architecture
# Starting from scratch with modern patterns

__version__ = "2.0.0-alpha"
__author__ = "RPG Engine Team"
__description__ = "Modern async-first RPG game engine"

# Core engine imports will be added as we build the system
from .core.engine import AsyncGameEngine
from .core.service_container import ServiceContainer
from .core.event_bus import EventBus

__all__ = [
    "AsyncGameEngine",
    "ServiceContainer", 
    "EventBus",
]
