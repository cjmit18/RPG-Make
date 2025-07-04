# game_sys/managers/action_queue.py
"""
Per-actor ActionQueue
---------------------
Stores timed actions (attack, cast, move, …) and advances them every tick.
TimeManager drives `tick(dt)`; game systems (combat, AI, input) call
`schedule()` to enqueue work.

Design
------
* A queue per actor (simple list ordered by remaining cooldown).
* Each entry: (action_name: str, payload: dict, t_remaining: float)
* When t_remaining <= 0 the entry is popped and returned by `consume(actor)`.
"""

from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:                       # avoids circulars at import time
    from game_sys.character.actor import Actor

ActionEntry = Tuple[str, dict[str, Any], float]   # (name, data, cooldown)


class ActionQueue:
    def __init__(self) -> None:
        self._queues: Dict[Actor, List[ActionEntry]] = defaultdict(list)

    # ------------------------------------------------------------------ #
    #  registration                                                      #
    # ------------------------------------------------------------------ #
    def register_actor(self, actor: "Actor") -> None:
        self._queues.setdefault(actor, [])

    # ------------------------------------------------------------------ #
    #  scheduling                                                        #
    # ------------------------------------------------------------------ #
    def schedule(
        self,
        actor: "Actor",
        name: str,
        cooldown: float,
        **kwargs,
    ) -> bool:
        """
        Enqueue an action for `actor` that becomes ready after `cooldown` sec.
        Returns False if an action with the same *name* is already waiting.
        """
        q = self._queues[actor]

        if any(entry[0] == name for entry in q):
            return False                           # already pending

        q.append((name, kwargs, cooldown))
        return True

    # ------------------------------------------------------------------ #
    #  time progression                                                  #
    # ------------------------------------------------------------------ #
    def tick(self, dt: float) -> None:
        """
        Reduce remaining time on every queued action.  Ready entries are
        flagged with 0 cooldown—`consume()` will pop them.
        """
        for q in self._queues.values():
            for idx, (name, data, rem) in enumerate(q):
                if rem > 0:
                    q[idx] = (name, data, max(0.0, rem - dt))

    # ------------------------------------------------------------------ #
    #  retrieval                                                         #
    # ------------------------------------------------------------------ #
    def consume(self, actor: "Actor") -> List[Tuple[str, dict[str, Any]]]:
        """
        Pop all ready actions for `actor` (where cooldown == 0).
        """
        q = self._queues.get(actor, [])
        ready: List[Tuple[str, dict[str, Any]]] = [
            (name, data) for (name, data, rem) in q if rem == 0
        ]
        self._queues[actor] = [entry for entry in q if entry[2] > 0]
        return ready


# ---------------------------------------------------------------------- #
#  factory                                                               #
# ---------------------------------------------------------------------- #
_DEFAULT_QUEUE: ActionQueue | None = None


def get_action_queue() -> ActionQueue:
    global _DEFAULT_QUEUE
    if _DEFAULT_QUEUE is None:
        _DEFAULT_QUEUE = ActionQueue()
    return _DEFAULT_QUEUE
