# game_sys/effects/statbuff.py

"""
Applies a temporary buff to a target’s stat for a duration.
"""

from typing import Any, Dict
from game_sys.effects.base import Effect
from game_sys.effects.status import StatusEffect
from game_sys.hooks.hooks import hook_dispatcher


class TemporaryStatBuff(Effect):
    def __init__(self, stat_name: str, amount: int, duration: int) -> None:
        self.stat_name = stat_name
        self.amount = amount
        self.duration = duration

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        return cls(
            stat_name=data.get("stat_name", ""),
            amount=int(data.get("amount", 0)),
            duration=int(data.get("duration", 0))
        )

    def apply(
        self,
        caster: Any,
        target: Any,
        combat_engine: Any = None
    ) -> str:
        buff = StatusEffect(
            name=f"Buff-{self.stat_name}-{self.amount}",
            stat_mods={self.stat_name: self.amount},
            duration=self.duration
        )
        target.add_status(buff)
        hook_dispatcher.fire("effect.apply", target=target, effect=buff)
        return f"{target.name} +{self.amount} {self.stat_name} for {self.duration} turns."
