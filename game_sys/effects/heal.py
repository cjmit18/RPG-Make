# game_sys/effects/heal.py

import random
from typing import Any, Dict, Union
from game_sys.effects.base import Effect

class HealEffect(Effect):
    """
    Instantly restores HP to the target (rolled if 'amount' is a dict).
    """

    def __init__(self, amount: int):
        self.amount = amount

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealEffect":
        """
        Build a HealEffect from JSON data. Accepts:
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

    def apply(self, caster: Any, target: Any, combat_engine: Any) -> str:
        """
        Heal 'target' by up to self.amount (clamped to max_health). Returns a log string.
        """
        healed = min(target.max_health, target.health + self.amount) - target.health
        target.health = min(target.max_health, target.health + self.amount)
        return f"{target.name} healed for {healed} HP."
