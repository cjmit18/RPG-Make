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
        slot = attrs.pop('slot', 'weapon')  # Extract slot or default to weapon
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            slot=slot,
            effect_ids=effect_ids,
            **attrs
        )
        self.base_damage = base_damage
        # Map the JSON string to the DamageType enum, default to PHYSICAL
        try:
            self.damage_type = DamageType[damage_type.upper()]
        except KeyError:
            self.damage_type = DamageType.PHYSICAL
        
        # Regular weapons cannot be dual wielded (only OffhandWeapons can)
        self.dual_wield = False

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


class OffhandWeapon(Weapon):
    """
    Offhand weapon: a weapon that can be dual-wielded in the offhand slot.
    
    JSON schema adds:
      dual_wield: bool (should be True for offhand weapons)
      damage_reduction: float (multiplier for offhand damage, default 0.5)
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        base_damage: float,
        effect_ids: list[str],
        damage_type: str = "PHYSICAL",
        dual_wield: bool = True,
        damage_reduction: float = 0.5,
        **attrs
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            base_damage=base_damage,
            effect_ids=effect_ids,
            damage_type=damage_type,
            **attrs
        )
        self.slot = "offhand"  # Override slot to offhand
        self.dual_wield = dual_wield
        self.damage_reduction = damage_reduction

    def get_effective_damage(self) -> float:
        """Get the effective damage when used in offhand."""
        return self.base_damage * self.damage_reduction

    def apply(self, user: Any, target: Any = None) -> None:
        """Equip as offhand weapon."""
        if hasattr(user, 'equip_offhand'):
            user.equip_offhand(self)
        else:
            # Fallback to regular equipment
            super().apply(user, target)

    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"OffhandWeapon (id={self.id}, name={self.name},\n "
            f"base_damage={self.base_damage}, "
            f"effective_damage={self.get_effective_damage()}, "
            f"damage_type={self.damage_type.name}, \n"
            f"dual_wield={self.dual_wield}, effects={self.effect_ids})"
        )


class TwoHandedWeapon(Weapon):
    """
    Two-handed weapon: a weapon that requires both hands and cannot be dual wielded.
    Examples: staves, great swords, two-handed axes, etc.
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
            base_damage=base_damage,
            effect_ids=effect_ids,
            damage_type=damage_type,
            **attrs
        )
        # Two-handed weapons explicitly cannot be dual wielded
        self.dual_wield = False
        self.two_handed = True

    def apply(self, user: Any, target: Any = None) -> None:
        """Equip as two-handed weapon, unequipping offhand if present."""
        super().apply(user, target)
        # Unequip offhand when wielding a two-handed weapon
        if hasattr(user, 'unequip_offhand'):
            user.unequip_offhand()

    def __str__(self) -> str:
        """String representation for debugging."""
        return (
            f"TwoHandedWeapon (id={self.id}, name={self.name}, "
            f"base_damage={self.base_damage}, "
            f"damage_type={self.damage_type.name}, "
            f"two_handed=True, effects={self.effect_ids})"
        )