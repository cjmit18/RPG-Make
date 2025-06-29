# game_sys/hooks/event_bus.py
"""
Module: game_sys.hooks.event_bus

Global EventBus with auto-detect for async/sync listeners.
"""
import asyncio
from typing import Any, Callable, Dict, List

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def on(self, event: str, listener: Callable[..., Any]):
        """Register a listener (sync or async) for an event."""
        self._listeners.setdefault(event, []).append(listener)

    def off(self, event: str, listener: Callable[..., Any]):
        """Remove a listener from an event."""
        if event in self._listeners:
            self._listeners[event] = [l for l in self._listeners[event] if l != listener]

    def emit(self, event: str, *args, **kwargs):
        """
        Emit an event to all listeners. Auto-detects coroutines:
        - Sync listeners are called immediately
        - Async listeners are scheduled on the current event loop
        """
        loop = asyncio.get_event_loop()
        for listener in list(self._listeners.get(event, [])):
            if asyncio.iscoroutinefunction(listener):
                loop.create_task(listener(*args, **kwargs))
            else:
                listener(*args, **kwargs)

# Instantiate global bus
event_bus = EventBus()
