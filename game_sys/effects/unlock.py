# game_sys/effects/unlock.py
from typing import Any
class UnlockEffect:
    """
    Allows opening locked chests/doors. Implementation depends on your world logic.
    """

    def __init__(self, target_type: str) -> None:
        self.target_type = target_type

    def apply(self, caster: Any, target: Any) -> None:
        # E.g. if target is a chest, set target.locked = False
        try:
            setattr(target, "locked", False)
        except Exception:
            pass
