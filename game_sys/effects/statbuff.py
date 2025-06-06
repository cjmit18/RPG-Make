# game_sys/effects/statbuff.py

from typing import Any, Dict
from game_sys.effects.base import Effect
from game_sys.effects.status import StatusEffect


class TemporaryStatBuff(Effect):
    """
    Applies a temporary buff to a target’s stat for a specified duration.
    JSON:
      {
        "type": "TemporaryStatBuff",
        "stat_name": "<stat>",
        "amount": <int>,
        "duration": <int>
      }
    """

    def __init__(self, stat_name: str, amount: int, duration: int):
        self.stat_name = stat_name
        self.amount = amount
        self.duration = duration

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemporaryStatBuff":
        stat_name = data.get("stat_name", "")
        amount = int(data.get("amount", 0))
        duration = int(data.get("duration", 0))
        return cls(stat_name, amount, duration)

    def apply(self, source: Any, target: Any, combat_engine: Any) -> str:
        """
        Internally creates a StatusEffect that adds stat_mods={stat_name: amount}
        for 'duration' turns.
        """
        buff_name = f"{source.name}-{self.stat_name}-{self.amount}-{self.duration}"
        status = StatusEffect(name=buff_name,
                              stat_mods={self.stat_name: self.amount},
                              duration=self.duration)
        try:
            target.add_status(status.name, status.stat_mods, status.duration)
        except AttributeError:
            if not hasattr(target, "status_effects"):
                target.status_effects = []
            target.status_effects.append(status)

        return f"{target.name} gains +{self.amount} {self.stat_name} for {self.duration} turns."
