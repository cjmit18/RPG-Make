# game_sys/items/item_base.py

"""
Base definitions for items: Item, EquipableItem, ConsumableItem, etc.
Refactored to include consumable __str__ overrides showing heal amounts.
"""
from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from game_sys.core.damage_types import DamageType
from game_sys.core.rarity import Rarity
from game_sys.core.experience import Levels

if TYPE_CHECKING:
    from game_sys.character.actor import Actor
    from game_sys.effects.base import Effect


def _format_effects(effects: List[Any]) -> List[str]:
    """
    Return a list of formatted effect descriptions safely.
    """
    out: List[str] = []
    for eff in effects:
        name = getattr(eff, 'name', None) or type(eff).__name__
        out.append(name)
    return out


def _format_damage_map(damage_map: Dict[DamageType, int]) -> List[str]:
    """
    Return a list of damage type strings.
    """
    return [f"{dt.name.capitalize()}: {amt}" for dt, amt in damage_map.items()]


class Item:
    """
    Core base class for any in-game item.
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        IID: Optional[uuid.UUID] = None
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.levels: Levels = Levels(self, level, 0)
        self.IID = IID or uuid.uuid4()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name!r}, level={self.levels.lvl}>"

    def __str__(self) -> str:
        parts: List[str] = []
        parts.append(f"{self.name} (ID={self.id})")
        parts.append(f"Level: {self.levels.lvl}")
        parts.append(f"Price: {self.price}")
        return " | ".join(parts)


class EquipableItem(Item):
    """
    Items that can be equipped.
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
        passive_effects: Optional[List[Any]],
        IID: Optional[uuid.UUID] = None
    ) -> None:
        super().__init__(id, name, description, price, level, IID)
        self.slot = slot
        self.grade = grade
        self.rarity = rarity
        self.base_bonus_ranges = base_bonus_ranges.copy()
        self.raw_damage_map = raw_damage_map.copy()
        self.percent_bonuses = percent_bonuses or {}
        self.passive_effects = passive_effects or []
        self.bonuses: Dict[str, int] = {}
        self.damage_map: Dict[DamageType, int] = {}

    def rescale(self, current_level: int) -> None:
        from random import randint
        from game_sys.core.scaler import scale_stat, scale_damage_map
        self.bonuses.clear()
        self.damage_map.clear()
        for stat, spec in self.base_bonus_ranges.items():
            lo, hi = spec.get('min', 0), spec.get('max', 0)
            rolled = scale_stat((lo, hi), current_level, grade=self.grade, rarity=self.rarity)
            self.bonuses[stat] = rolled
        raw = {dt_str.upper(): randint(spec.get('min',0), spec.get('max',0))
               for dt_str, spec in self.raw_damage_map.items()}
        scaled = scale_damage_map(raw, current_level, grade=self.grade, rarity=self.rarity)
        from game_sys.core.damage_types import DamageType as DT
        for dt_str, amt in scaled.items():
            try:
                self.damage_map[DT[dt_str]] = amt
            except KeyError:
                pass

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name!r}, slot={self.slot}>"


class ConsumableItem(Item):
    """
    Items that can be consumed for effects.
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
        amount: Optional[int] = None,
        IID: Optional[uuid.UUID] = None
    ) -> None:
        super().__init__(id, name, description, price, level, IID)
        from game_sys.effects.base import Effect
        self.effects: List[Effect] = [Effect.from_dict(e) for e in effects_data]
        # Determine fixed amount if single Heal effect
        self.amount = None
        if len(self.effects) == 1:
            eff = self.effects[0]
            self.amount = getattr(eff, 'amount', None)

    def apply(self, actor: Actor, combat_engine: Any = None) -> str:
        messages: List[str] = []
        for eff in self.effects:
            try:
                msg = eff.apply(actor, actor, combat_engine)
            except TypeError:
                msg = eff.apply(actor)
            messages.append(msg)
        return "; ".join(messages)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name!r}, amount={self.amount}>"

    def __str__(self) -> str:
        base = super().__str__()
        if self.amount is not None:
            base += f" | Amount: {self.amount}"
        return base
