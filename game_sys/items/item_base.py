# game_sys/items/item_base.py

from typing import Dict, List, Optional, Any, TYPE_CHECKING
import uuid
from game_sys.core.damage_types import DamageType
from game_sys.core.rarity import Rarity
from game_sys.core.experience import Levels

if TYPE_CHECKING:
    from game_sys.character.actor import Actor


def _format_effects(effects: List[Any]) -> List[str]:
    """
    Return a list of formatted effect descriptions.
    """
    out = []
    for eff in effects:
        name = type(eff).__name__
        if hasattr(eff, 'amount'):
            out.append(f"{name}: {eff.amount}")
        else:
            out.append(name)
    return out


def _format_damage_map(damage_map: Dict[DamageType, int]) -> List[str]:
    """
    Return a list of damage type strings.
    """
    return [
        f"{dtype.name.capitalize()}: {amt}"
        for dtype, amt in damage_map.items()
    ]


class Item:
    """
    Base class for all items.
    """

    def __init__(
            self,
            id: str,
            name: str,
            description: str,
            price: int,
            level: int,
            IID: uuid.UUID
            ):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.level: Levels = Levels(self, level, 0)
        self.IID = IID or uuid.uuid4()

    def __repr__(self) -> str:
        return (f"<{type(self).__name__}\
                 name={self.name!r},\
                 level={self.level.lvl}>")

    def __str__(self) -> str:
        rarity = getattr(self, 'rarity', Rarity.COMMON)
        lines: List[str] = []
        # Header
        lines.append(f"{self.name} (ID: {self.id})")
        # Basic info
        lines.append(f"  Level: {self.level.lvl}")
        lines.append(f"  Price: {self.price} gold")
        lines.append(f"  Rarity: {rarity.name.capitalize()}")
        lines.append(f"  Grade: {getattr(self, 'grade', 0)}")
        lines.append(f"  Description: {self.description}")

        # Consumable effects
        if hasattr(self, 'effects'):
            effs = _format_effects(self.effects)
            lines.append("Effects:")
            for e in effs:
                lines.append(f"    - {e}")

        # Equipable stats
        if hasattr(self, 'slot'):
            lines.append(f"Slot: {self.slot}")
            # Flat bonuses
            if getattr(self, 'bonuses', None):
                lines.append("Bonuses:")
                for stat, val in self.bonuses.items():
                    lines.append(f"    - {stat.capitalize()}: {val}")
            # Percent bonuses
            if getattr(self, 'percent_bonuses', None):
                lines.append("Percent Bonuses:")
                for stat, pct in self.percent_bonuses.items():
                    lines.append(f"    - {stat.capitalize()}: +{pct}%")
            # Damage map
            if getattr(self, 'damage_map', None):
                dmg_lines = _format_damage_map(self.damage_map)
                lines.append("Damage:")
                for d in dmg_lines:
                    lines.append(f"    - {d}")
            # Passive effects
            if getattr(self, 'passive_Effects', None):
                lines.append("Passive Effects:")
                for pe in self.passive_Effects:
                    lines.append(f"    - {pe}")
            # Enchantable flag
            lines.append(f"Enchantable: {'Yes' if getattr(
                self, 'is_enchantable', False) else 'No'}")

        return "\n".join(lines)

    @staticmethod
    def view_item(item: "Item") -> str:
        return str(item)


class EquipableItem(Item):
    """
    Equipable item: holds stat bonuses and passive effects.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        slot: str,
        grade: int,
        rarity: Rarity,
        base_bonus_ranges: Dict[str, Dict[str, int]],
        raw_damage_map: Dict[str, Dict[str, int]],
        is_enchantable: bool,
        percent_bonuses: Optional[Dict[str, float]],
        passive_Effects: Optional[List[Dict[str, Any]]],
        IID: uuid.UUID
    ):
        super().__init__(id, name, description, price, level, IID)
        self.slot = slot
        self.grade = grade
        self.rarity = rarity
        self.is_enchantable = is_enchantable

        # Base definitions
        self.base_bonus_ranges = base_bonus_ranges.copy()
        self.raw_damage_map = raw_damage_map.copy()

        # Computed values
        self.bonuses: Dict[str, int] = {}
        self.percent_bonuses = percent_bonuses or {}
        self.damage_map: Dict[DamageType, int] = {}
        self.passive_Effects = passive_Effects or []

    def rescale(self, current_level: int) -> None:
        """
        Recompute bonuses and damage_map based on level, grade, and rarity.
        """
        from random import randint
        from game_sys.core.scaler import scale_stat, scale_damage_map

        # Clear previous
        self.bonuses.clear()
        self.damage_map.clear()

        # Flat bonuses
        for stat, spec in self.base_bonus_ranges.items():
            lo = spec.get('min', 0)
            hi = spec.get('max', lo)
            rolled = scale_stat(
                                (lo, hi),
                                current_level,
                                grade=self.grade,
                                rarity=self.rarity
                                )
            # apply percent buffs later
            self.bonuses[stat] = rolled

        # Raw damage roll
        raw_rolls: Dict[str, int] = {}
        for dt_str, spec in self.raw_damage_map.items():
            lo = spec.get('min', 0)
            hi = spec.get('max', lo)
            raw_rolls[dt_str.upper()] = randint(lo, hi)

        # Scale damage_map
        scaled = scale_damage_map(
            raw_rolls,
            current_level,
            grade=self.grade,
            rarity=self.rarity
            )
        for dt_str, amt in scaled.items():
            try:
                dt = DamageType[dt_str.upper()]
                self.damage_map[dt] = amt
            except KeyError:
                continue

        # Percent bonuses
        for stat, pct in self.percent_bonuses.items():
            base = self.bonuses.get(stat, 0)
            self.bonuses[stat] = int(round(base * (1 + pct / 100.0)))

    def __repr__(self) -> str:
        return f"<EquipableItem name={self.name!r}, slot={self.slot}>"


class ConsumableItem(Item):
    """
    Consumable: applies effects when used.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        effects_data: List[Dict[str, Any]],
        grade: int,
        rarity: Rarity,
        IID: uuid.UUID
    ):
        super().__init__(id, name, description, price, level, IID)
        from game_sys.effects.base import Effect
        self.effects: List[Any] = [Effect.from_dict(e) for e in effects_data]

    def apply(self, actor: "Actor", combat_engine) -> str:
        logs = []
        for eff in self.effects:
            logs.append(eff.apply(actor, actor, combat_engine))
        return "\n".join(logs)

    def __repr__(self) -> str:
        return (
                f"<ConsumableItem name={self.name!r},\
                effects={len(self.effects)}>"
                )
