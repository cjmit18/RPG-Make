# game_sys/effects/instant.py

import random
from typing import Any, Dict
from game_sys.effects.base import Effect


class InstantHeal(Effect):
    """
    Applies a flat amount of healing to the target (rolled if 'amount' is a dict).
    """

    def __init__(self, amount: int):
        self.amount = amount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstantHeal":
        """
        Build from JSON data. Accepts:
          - "amount": <int>            → heals exactly that amount
          - "amount": { "min": X, "max": Y } → heals random int in [X, Y]
        """
        amt_spec = data.get("amount", 0)
        if isinstance(amt_spec, dict):
            lo = int(amt_spec.get("min", 0))
            hi = int(amt_spec.get("max", lo))
            amount = random.randint(lo, hi)
        else:
            amount = int(amt_spec)
        return cls(amount)

    def apply(self, source: Any, target: Any, combat_engine: Any) -> str:
        healed = min(target.max_health, target.health + self.amount) - target.health
        target.health = min(target.max_health, target.health + self.amount)
        return f"{target.name} healed for {healed} HP."


class InstantMana(Effect):
    """
    Applies a flat amount of mana restoration to the target (rolled if dict).
    """

    def __init__(self, amount: int):
        self.amount = amount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstantMana":
        """
        Build from JSON data. Accepts:
          - "amount": <int>            → restore exactly that amount
          - "amount": { "min": X, "max": Y } → restore random int in [X, Y]
        """
        amt_spec = data.get("amount", 0)
        if isinstance(amt_spec, dict):
            lo = int(amt_spec.get("min", 0))
            hi = int(amt_spec.get("max", lo))
            amount = random.randint(lo, hi)
        else:
            amount = int(amt_spec)
        return cls(amount)

    def apply(self, source: Any, target: Any, combat_engine: Any) -> str:
        restored = min(target.max_mana, target.mana + self.amount) - target.mana
        target.mana = min(target.max_mana, target.mana + self.amount)
        return f"{target.name} restored {restored} MP."
