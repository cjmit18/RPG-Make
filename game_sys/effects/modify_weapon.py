# game_sys/effects/modify_weapon.py

from typing import Any, Dict
from game_sys.effects.base import Effect


class ModifyWeaponDamageEffect(Effect):
    """
    Buffs a character’s weapon damage by a percentage.
    JSON:
      {
        "type": "ModifyWeaponDamage",
        "weapon_type": "<slot_name>",
        "percent_bonus": <float>
      }
    """

    def __init__(self, weapon_type: str, percent_bonus: float) -> None:
        self.weapon_type = weapon_type
        self.percent_bonus = percent_bonus

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModifyWeaponDamageEffect":
        weapon_type = data.get("weapon_type", "")
        percent_bonus = float(data.get("percent_bonus", 0.0))
        return cls(weapon_type, percent_bonus)

    def apply(self, caster: Any, target: Any, combat_engine: Any) -> str:
        """
        If 'target' has an equipped weapon matching weapon_type, increase its damage.
        """
        if hasattr(target, "weapon") and getattr(target.weapon, "type", "") == self.weapon_type:
            original_damage = getattr(target.weapon, "damage", 0)
            bonus_damage = int(round(original_damage * (self.percent_bonus / 100.0)))
            target.weapon.damage = original_damage + bonus_damage
            return f"{target.name}'s {self.weapon_type} damage increased by {bonus_damage}."
        else:
            return f"{target.name} does not have a {self.weapon_type} equipped."
