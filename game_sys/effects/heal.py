# game_sys/effects/heal.py

"""
Implements a HealEffect that restores HP to a target,
either a fixed amount or a random range.
"""

import random
from typing import Any, Dict
from game_sys.effects.base import Effect
from game_sys.hooks.hooks import hook_dispatcher


class HealEffect(Effect):
    """
    Instantly restores HP to the target.
    """

    def __init__(self, amount: int) -> None:
        self.amount = amount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Effect:
        amt = data.get("amount", 0)
        if isinstance(amt, dict):
            lo, hi = int(amt.get("min", 0)), int(amt.get("max", 0))
            amount = random.randint(lo, hi)
        else:
            amount = int(amt)
        return cls(amount)

    def apply(
        self,
        caster: Any,
        target: Any,
        combat_engine: Any = None
    ) -> str:
        before = target.current_health
        target.current_health = before + self.amount
        healed = target.current_health - before
        hook_dispatcher.fire("effect.apply", target=target, effect=self)
        return f"{target.name} healed for {healed} HP."
