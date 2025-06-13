# game_sys/effects/modify_weapon.py

"""
Buffs a character’s weapon damage by a percentage.
"""

from typing import Any, Dict
from game_sys.effects.base import Effect
from game_sys.core.hooks import hook_dispatcher

class ModifyWeaponDamageEffect(Effect):
    def __init__(self, weapon_type: str, percent_bonus: float) -> None:
        self.weapon_type = weapon_type
        self.percent_bonus = percent_bonus

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        return cls(
            weapon_type=data.get("weapon_type", ""),
            percent_bonus=float(data.get("percent_bonus", 0.0))
        )

    def apply(
        self,
        caster: Any,
        target: Any,
        combat_engine: Any = None
    ) -> str:
        weapon = getattr(target, "weapon", None)
        if weapon and getattr(weapon, "type", "") == self.weapon_type:
            orig = getattr(weapon, "damage", 0)
            bonus = int(round(orig * (self.percent_bonus / 100)))
            weapon.damage = orig + bonus
            hook_dispatcher.fire("effect.apply", target=target, effect=self)
            return f"{target.name}'s {self.weapon_type} damage +{bonus}."
        return f"{target.name} has no {self.weapon_type} equipped."
