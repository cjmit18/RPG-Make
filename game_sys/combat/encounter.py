# game_sys/combat/encounter.py

"""
Encounter wraps CombatEngine for backward compatibility. It retains the same
interface (start() returning a result string), but delegates the fight logic
to CombatEngine.
"""

from typing import List, Union, Optional, Callable
import random
from game_sys.core.actor import Actor
from game_sys.combat.combat_engine import CombatEngine

class Encounter:
    """
    Thin wrapper around CombatEngine. Accepts the same constructor args,
    but simply calls engine.run() from start().
    """

    def __init__(
        self,
        party: Union[Actor, List[Actor]],
        enemies: Union[Actor, List[Actor]],
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable[[Actor], str]] = None,
        max_turns: int = 100,
    ):
        self.engine = CombatEngine(
            party=party,
            enemies=enemies,
            rng=rng,
            action_fn=action_fn,
            max_turns=max_turns,
        )

    def start(self) -> str:
        return self.engine.run()
