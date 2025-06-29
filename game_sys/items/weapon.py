# game_sys/items/weapon.py

from typing import Any
from game_sys.items.equipment import Equipment
from game_sys.core.damage_types import DamageType


class Weapon(Equipment):
    """
    Weapon item: does damage when wielded.

    JSON schema adds:
      base_damage: float
      damage_type: str (one of DamageType names; defaults to PHYSICAL)
      effect_ids: List[str] of on-hit effects
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        base_damage: float,
        effect_ids: list[str],
        damage_type: str = "PHYSICAL",
        **attrs
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            slot="weapon",
            stats={},
            effect_ids=effect_ids,
            **attrs
        )
        self.base_damage = base_damage
        # Map the JSON string to the DamageType enum, default to PHYSICAL
        try:
            self.damage_type = DamageType[damage_type.upper()]
        except KeyError:
            self.damage_type = DamageType.PHYSICAL

    def apply(self, user: Any, target: Any = None) -> None:
        """Equip as weapon."""
        super().apply(user, target)
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"Weapon (id={self.id}, name={self.name},\n "
            f"base_damage={self.base_damage}, damage_type={self.damage_type.name}, \n"
            f"effects={self.effect_ids})"
        )