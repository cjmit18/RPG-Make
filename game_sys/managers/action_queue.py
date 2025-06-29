# game_sys/managers/action_queue.py
"""
Module: game_sys.managers.action_queue

Schedules and processes time-based actions for actors.
"""
import time
from typing import Any, Dict, List, Tuple

class ActionQueue:
    """
    Manages a queue of scheduled actions per actor, executing them when ready.
    """
    def __init__(self):
        self._pending: Dict[Any, List[Tuple[float, str, Dict]]] = {}
        self._ready:   Dict[Any, List[Tuple[str, Dict]]] = {}

    def register_actor(self, actor: Any):
        """Initialize queues for a new actor."""
        self._pending.setdefault(actor, [])
        self._ready.setdefault(actor, [])

    def schedule(self, actor: Any, action_name: str, cooldown: float, **params) -> bool:
        """
        Schedule an action to occur after a cooldown (in seconds).
        Returns True if scheduled successfully.
        """
        fire_time = time.time() + cooldown
        self._pending.setdefault(actor, []).append((fire_time, action_name, params))
        return True

    def consume(self, actor: Any) -> List[Tuple[str, Dict]]:
        """
        Retrieve and clear all ready actions for an actor.
        """
        ready = list(self._ready.get(actor, []))
        self._ready[actor] = []
        return ready

    def tick(self, dt: float):
        """
        Move actions whose scheduled time has passed into the ready queue.
        """
        now = time.time()
        for actor, pending_list in list(self._pending.items()):
            for fire_time, action_name, params in list(pending_list):
                if now >= fire_time:
                    self._ready.setdefault(actor, []).append((action_name, params))
                    pending_list.remove((fire_time, action_name, params))
