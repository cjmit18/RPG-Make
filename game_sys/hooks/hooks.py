# game_sys/core/hooks.py
from collections import defaultdict
from typing import Any, Callable

class HookDispatcher:
    """
    A simple event dispatcher that allows registering listeners
    for specific events and firing those events
    with optional keyword arguments.
    """
    def __init__(self):
        self._listeners: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def register(self, event: str, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Register a listener for `event` and return the handler
        so callers can store it for later unregistration.
        """
        self._listeners[event].append(fn)
        return fn

    def unregister(self, event: str, fn: Callable[..., Any]) -> None:
        """
        Remove a previously-registered listener so it no longer fires.
        """
        if fn in self._listeners.get(event, []):
            self._listeners[event].remove(fn)

    def fire(self, event: str, **kwargs: Any) -> None:
        """
        Invoke all listeners registered for `event`, passing along kwargs.
        """
        for fn in list(self._listeners.get(event, [])):
            fn(**kwargs)

hook_dispatcher = HookDispatcher()
