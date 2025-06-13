# game_sys/effects/unlock.py

"""
Allows opening locked chests/doors.
"""

from typing import Any, Dict
from game_sys.effects.base import Effect
from game_sys.core.hooks import hook_dispatcher

class UnlockEffect(Effect):
    def __init__(self, target_type: str) -> None:
        self.target_type = target_type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        return cls(target_type=data.get("target_type", ""))

    def apply(
        self,
        caster: Any,
        target: Any,
        combat_engine: Any = None
    ) -> str:
        hook_dispatcher.fire("effect.apply", target=target, effect=self)
        try:
            setattr(target, "locked", False)
            return f"{caster.name} unlocks {self.target_type}."
        except Exception:
            return f"{caster.name} failed to unlock {self.target_type}."
