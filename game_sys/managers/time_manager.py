# game_sys/managers/time_manager.py
"""
Module: game_sys.managers.time_manager

An asyncio-compatible timekeeping system. Schedules periodic ticks
for registered subsystems using asyncio Tasks.
"""
import asyncio
from typing import List, Protocol

# Protocol for tickable subsystems
class Tickable(Protocol):
    def tick(self, dt: float): ...

class AsyncTimeManager:
    """
    Drives the game clock and updates registered tickables asynchronously.

    Usage:
        time_manager = AsyncTimeManager()
        time_manager.register(subsystem)
        time_manager.start(interval=1/60)
        # on shutdown: time_manager.stop()
    """
    def __init__(self):
        self._tickables: List[Tickable] = []
        self._task: asyncio.Task | None = None
        self._running = False

    def register(self, tickable: Tickable):
        """Subscribe a subsystem for update ticks."""
        if tickable not in self._tickables:
            self._tickables.append(tickable)

    def unregister(self, tickable: Tickable):
        """Unsubscribe a subsystem from update ticks."""
        if tickable in self._tickables:
            self._tickables.remove(tickable)

    async def run(self, interval: float = 1/60):
        """Async loop invoking tick(dt) on each registered subsystem."""
        if self._running:
            return
        self._running = True
        loop = asyncio.get_event_loop()
        last = loop.time()
        try:
            while self._running:
                now = loop.time()
                dt = now - last
                last = now
                for t in list(self._tickables):
                    try:
                        t.tick(dt)
                    except Exception:
                        continue
                await asyncio.sleep(interval)
        finally:
            self._running = False

    def start(self, interval: float = 1/60):
        """Start the async ticking loop in background."""
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self.run(interval))

    def stop(self):
        """Stop the ticking loop and cancel the background task."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

# Global TimeManager instance
from game_sys.effects.status_manager import status_manager

time_manager = AsyncTimeManager()
# Always register status effects manager
time_manager.register(status_manager)
