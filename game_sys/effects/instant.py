# game_sys/effects/instant.py

"""
InstantHeal and InstantMana effects for immediate resource restoration.
"""

import random
from typing import Any, Dict
from game_sys.effects.base import Effect
from game_sys.hooks.hooks import hook_dispatcher


class InstantHeal(Effect):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        amt = data.get("amount", 0)
        if isinstance(amt, dict):
            lo, hi = int(amt.get("min", 0)), int(amt.get("max", lo))
            amount = random.randint(lo, hi)
        else:
            amount = int(amt)
        return cls(amount)

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        before = target.current_health
        target.current_health = before + self.amount
        healed = target.current_health - before
        hook_dispatcher.fire("effect.apply", target=target, effect=self)
        return f"{target.name} healed for {healed} HP."

class InstantMana(Effect):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstantMana":
        amt = data.get("amount", 0)
        if isinstance(amt, dict):
            lo, hi = int(amt.get("min", 0)), int(amt.get("max", lo))
            amount = random.randint(lo, hi)
        else:
            amount = int(amt)
        return cls(amount)

    def apply(self, caster: Any, target: Any, combat_engine: Any = None) -> str:
        before = target.current_mana
        target.current_mana = before + self.amount
        restored = target.current_mana - before
        hook_dispatcher.fire("effect.apply", target=target, effect=self)
        return f"{target.name} restored {restored} MP."
