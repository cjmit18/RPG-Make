# game_sys/hooks/event_bus.py
"""
Module: game_sys.hooks.event_bus

Global EventBus with auto-detect for async/sync listeners.
"""
import asyncio
from typing import Any, Callable, Dict, List
from game_sys.logging import hooks_logger, log_exception

class EventBus:
    async def emit_async(self, event: str, *args, **kwargs):
        """
        Awaitable version of emit: awaits all async listeners, calls sync listeners immediately.
        Returns when all listeners have completed.
        """
        listener_count = len(self._listeners.get(event, []))
        hooks_logger.debug(
            f"[async] Emitting event '{event}' to {listener_count} listeners"
        )
        tasks = []
        for listener in list(self._listeners.get(event, [])):
            if asyncio.iscoroutinefunction(listener):
                tasks.append(listener(*args, **kwargs))
            else:
                hooks_logger.debug(f"[async] Calling sync listener {listener.__name__}")
                listener(*args, **kwargs)
        if tasks:
            await asyncio.gather(*tasks)

    def once(self, event: str, listener: Callable[..., Any]):
        """
        Register a one-time listener for an event. Listener is removed after first call.
        """
        def wrapper(*args, **kwargs):
            self.off(event, wrapper)
            return listener(*args, **kwargs)
        self.on(event, wrapper)

    def on_pre(self, event: str, listener: Callable[..., Any]):
        """
        Register a listener to run before the main event listeners (pre-hook).
        """
        self.on(f"pre_{event}", listener)

    def on_post(self, event: str, listener: Callable[..., Any]):
        """
        Register a listener to run after the main event listeners (post-hook).
        """
        self.on(f"post_{event}", listener)

    def emit_with_hooks(self, event: str, *args, **kwargs):
        """
        Emit pre-event, main event, and post-event hooks in order (sync).
        """
        self.emit(f"pre_{event}", *args, **kwargs)
        self.emit(event, *args, **kwargs)
        self.emit(f"post_{event}", *args, **kwargs)

    async def emit_with_hooks_async(self, event: str, *args, **kwargs):
        """
        Awaitable version: emits pre-event, main event, and post-event hooks in order.
        """
        await self.emit_async(f"pre_{event}", *args, **kwargs)
        await self.emit_async(event, *args, **kwargs)
        await self.emit_async(f"post_{event}", *args, **kwargs)
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
