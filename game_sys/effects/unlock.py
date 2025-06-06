# game_sys/effects/unlock.py

from typing import Any, Dict
from game_sys.effects.base import Effect


class UnlockEffect(Effect):
    """
    Allows opening locked chests/doors. JSON:
      {
        "type": "Unlock",
        "target_type": "<identifier_of_lock>"
      }
    """

    def __init__(self, target_type: str) -> None:
        self.target_type = target_type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnlockEffect":
        target_type = data.get("target_type", "")
        return cls(target_type)

    def apply(self, caster: Any, target: Any, combat_engine: Any) -> str:
        """
        Attempts to set target.locked = False. Returns success/failure.
        """
        try:
            setattr(target, "locked", False)
            return f"{caster.name} unlocks {self.target_type}."
        except Exception:
            return f"{caster.name} failed to unlock {self.target_type}."
