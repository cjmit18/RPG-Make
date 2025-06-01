# game_sys/effects/modify_weapon.py
from __future__ import annotations
from typing import Any
class ModifyWeaponDamageEffect:
    """
    Permanently (or temporarily) buff a character’s weapon damage by a percentage.
    """

    def __init__(self, weapon_type: str, percent_bonus: float) -> None:
        self.weapon_type = weapon_type
        self.percent_bonus = percent_bonus

    def apply(self, caster: Any, target: Any) -> None:
        # Implementation detail:
        #   You could store this buff in caster.statuses or caster.stats,
        #   but for now assume it hooks into your combat engine directly.
        pass
