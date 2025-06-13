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
        self._listeners: dict[str, list[Callable[..., Any]]] = defaultdict(
            list
        )

    def register(self, event: str, fn: Callable[..., Any]) -> None:
        self._listeners[event].append(fn)

    def fire(self, event: str, **kwargs: Any) -> None:
        for fn in self._listeners.get(event, []):
            fn(**kwargs)


hook_dispatcher = HookDispatcher()
