from typing import Dict, List, Optional, Union, Any
from game_sys.core.rarity import Rarity
from game_sys.core.damage_types import DamageType
from game_sys.enchantments.base import BasicEnchantment

class Item:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        grade: int = 1,
        rarity: Union[Rarity, str] = Rarity.COMMON,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.level = level
        self.grade = grade
        self.rarity = rarity if isinstance(rarity, Rarity) else Rarity[rarity.upper()]

    def __str__(self):
        return f"{self.name} (Level {self.level})"


class EquipableItem(Item):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        slot: str,
        grade: int = 1,
        rarity: Union[Rarity, str] = Rarity.COMMON,
        base_bonus_ranges: Optional[Dict[str, Dict[str, int]]] = None,
        damage_map: Optional[Dict[str, Dict[str, int]]] = None,
        percent_bonuses: Optional[Dict[str, float]] = None,
        passive_effects: Optional[List[str]] = None,
        enchantments: Optional[List[BasicEnchantment]] = None,
        resistances: Optional[Dict[DamageType, float]] = None,
    ):
        super().__init__(id, name, description, price, level, grade, rarity)
        self.slot = slot
        self.base_bonus_ranges = base_bonus_ranges or {}
        self.damage_map = damage_map or {}
        self.percent_bonuses = percent_bonuses or {}
        self.passive_effects = passive_effects or []
        self.enchantments = enchantments or []
        self.resistances = resistances or {}
        self.bonuses = self._calculate_bonus_totals()

    def _calculate_bonus_totals(self) -> Dict[str, int]:
        totals: Dict[str, int] = {}
        for stat, range_dict in self.base_bonus_ranges.items():
            amt = int(range_dict.get("min", 0))
            totals[stat] = totals.get(stat, 0) + amt

        for ench in self.enchantments:
            for stat, value in ench.stat_bonuses.items():
                totals[stat] = totals.get(stat, 0) + value

        return totals

    def total_damage_map(self) -> Dict[DamageType, int]:
        final: Dict[DamageType, int] = {}
        for dt_name, dmg_dict in self.damage_map.items():
            try:
                dt = DamageType[dt_name.upper()]
                avg = int((dmg_dict.get("min", 0) + dmg_dict.get("max", 0)) / 2)
                if avg > 0:
                    final[dt] = avg
            except KeyError:
                continue

        for ench in self.enchantments:
            for dt, val in ench.damage_modifiers.items():
                final[dt] = final.get(dt, 0) + val

        return final

    def __str__(self):
        lines = [
            f"| Item: {self.name} (ID: {self.id})",
            f"| Level: {self.level} | Price: {self.price}",
            f"| Description: {self.description}",
            f"| Slot: {self.slot} | Grade: {self.grade} | Rarity: {self.rarity.name}"
        ]
        if self.bonuses:
            lines.append("| Bonuses: " + ", ".join(f"{k}: {v}" for k, v in self.bonuses.items()))

        total_dmg = self.total_damage_map()
        if total_dmg:
            dmg_str = ", ".join(f"{dt.name}: {val}" for dt, val in total_dmg.items())
            lines.append(f"| Damage: {dmg_str}")

        if self.resistances:
            res_str = ", ".join(f"{dt.name}: {mult:.2f}" for dt, mult in self.resistances.items())
            lines.append(f"| Resistances: {res_str}")

        if self.enchantments:
            lines.append("| Enchantments:")
            for ench in self.enchantments:
                lines.append(str(ench))

        return "\n".join(lines)


class ConsumableItem(Item):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        effects_data: List[Dict[str, Any]],
        amount: int = 1,
        grade: int = 1,
        rarity: Union[Rarity, str] = Rarity.COMMON,
    ):
        super().__init__(id, name, description, price, level, grade, rarity)
        self.effects_data = effects_data
        self.amount = amount

    def __str__(self):
        return f"{self.name} x{self.amount} (Restores effects: {len(self.effects_data)})"
