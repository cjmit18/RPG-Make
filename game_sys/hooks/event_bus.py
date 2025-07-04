# game_sys/hooks/event_bus.py
"""
Module: game_sys.hooks.event_bus

Global EventBus with auto-detect for async/sync listeners.
"""
import asyncio
from typing import Any, Callable, Dict, List
from game_sys.logging import hooks_logger, log_exception

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}
        hooks_logger.debug("EventBus initialized")

    def on(self, event: str, listener: Callable[..., Any]):
        """Register a listener (sync or async) for an event."""
        self._listeners.setdefault(event, []).append(listener)
        hooks_logger.debug(
            f"Registered listener {listener.__name__} for event '{event}'"
        )

    def off(self, event: str, listener: Callable[..., Any]):
        """Remove a listener from an event."""
        if event in self._listeners:
            self._listeners[event] = [l for l in self._listeners[event] if l != listener]
            hooks_logger.debug(
                f"Removed listener {listener.__name__} from event '{event}'"
            )

    @log_exception
    def emit(self, event: str, *args, **kwargs):
        """
        Emit an event to all listeners. Auto-detects coroutines:
        - Sync listeners are called immediately
        - Async listeners are scheduled on the current event loop
        """
        listener_count = len(self._listeners.get(event, []))
        hooks_logger.debug(
            f"Emitting event '{event}' to {listener_count} listeners"
        )
        
        for listener in list(self._listeners.get(event, [])):
            if asyncio.iscoroutinefunction(listener):
                try:
                    hooks_logger.debug(
                        f"Scheduling async listener {listener.__name__}"
                    )
                    loop = asyncio.get_running_loop()
                    loop.create_task(listener(*args, **kwargs))
                except RuntimeError:
                    # No event loop running, create a new one
                    hooks_logger.debug(
                        f"No event loop, running async listener {listener.__name__}"
                    )
                    asyncio.run(listener(*args, **kwargs))
            else:
                hooks_logger.debug(f"Calling sync listener {listener.__name__}")
                listener(*args, **kwargs)


# Instantiate global bus
event_bus = EventBus()
