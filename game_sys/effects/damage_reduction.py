# game_sys/effects/damage_reduction.py

"""
Reduces incoming damage by a fixed percentage for `duration` turns.
Wraps into a StatusEffect so Actor.take_damage sees it.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
from game_sys.effects.status import StatusEffect, Effect
from game_sys.core.hooks import hook_dispatcher

if TYPE_CHECKING:
    from game_sys.character.actor import Actor


class DamageReductionEffect(Effect):
    """
    Reduces incoming damage by a fixed percentage.
    """

    def __init__(self, percent: int, duration: int, target_side: str = "Enemy") -> None:
        self.percent = percent
        self.duration = duration
        self.target_side = target_side

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Effect:
        return cls(
            percent=int(data.get("percent", 0)),
            duration=int(data.get("duration", 0)),
            target_side=data.get("target", "Enemy")
        )

    def apply(self, caster: Actor, target: Actor, combat_engine: Any = None) -> str:
        actual = caster if self.target_side.lower() == "self" else target
        status = StatusEffect(
            name="DamageReduction",
            stat_mods={"DamageReduction": self.percent},
            duration=self.duration
        )
        actual.add_status(status)
        hook_dispatcher.fire("effect.apply", target=actual, effect=status)
        return f"{actual.name} gains {self.percent}% damage reduction for {self.duration} turns."
