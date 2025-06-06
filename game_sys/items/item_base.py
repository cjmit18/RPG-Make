# game_sys/items/item_base.py

from typing import Dict, List, Optional, Any, TYPE_CHECKING
import random

from game_sys.core.damage_types import DamageType
from game_sys.items.rarity import Rarity
from game_sys.items.scaler import scale_stat, scale_damage_map
from game_sys.core.experience_functions import Levels

if TYPE_CHECKING:
    # Only for type hints; actual imports happen inside methods
    from game_sys.core.actor import Actor
    from game_sys.effects.base import Effect


class Item:
    """
    Base class for all items (Equipable or Consumable).
    """

    def __init__(self, id: str, name: str, description: str, price: int, level: int):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.price: int = price
        self.level: Levels = Levels(self, level, 0)  # store price as experience placeholder

    def __repr__(self):
        return f"<Item id={self.id!r}, level={self.level.lvl}>"

    def __str__(self):
        return f"{self.name} (lvl {self.level.lvl})"


class EquipableItem(Item):
    """
    An item that can be equipped by a character. Supports:
      - grade & rarity scaling
      - base bonuses (e.g. {"attack": {"min":1,"max":3}})
      - raw damage map (e.g. {"PHYSICAL": {"min":2,"max":5}})
      - percent bonuses (e.g. {"attack": 10})
      - passive_Effects: a list of JSON‐dicts, each representing an Effect to add when equipped
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
        percent_bonuses: Optional[Dict[str, float]] = None,
        passive_Effects: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(id, name, description, price, level)

        self.slot: str = slot  # e.g. "weapon", "armor", "amulet", etc.
        self.grade: int = grade
        self.rarity: Rarity = rarity
        self.is_enchantable: bool = is_enchantable

        # Base‐range dicts from JSON, before scaling
        #   e.g. {"attack": {"min":1,"max":3}, ...}
        self.base_bonus_ranges: Dict[str, Dict[str, int]] = base_bonus_ranges.copy()
        #   e.g. {"PHYSICAL": {"min":2,"max":5}, ...}
        self.raw_damage_map: Dict[str, Dict[str, int]] = raw_damage_map.copy()

        # After scaling, these two hold final numerical values:
        self.bonuses: Dict[str, int] = {}
        self.damage_map: Dict[DamageType, int] = {}

        # Percent bonuses applied after numeric scaling:
        #   e.g. {"attack": 10} means +10% to final 'attack' bonus
        self.percent_bonuses: Dict[str, float] = percent_bonuses.copy() if percent_bonuses else {}

        # Passive effects to apply when equipped (list of JSON dicts)
        self.passive_Effects: List[Dict[str, Any]] = passive_Effects.copy() if passive_Effects else []

        # Track whether this item has been enchanted (if your code uses that)
        self.is_enchanted: bool = False

    def rescale(self, current_level: int) -> None:
        """
        Recompute:
          - self.bonuses: Dict[str, int]
          - self.damage_map: Dict[DamageType, int]
        using scale_stat and scale_damage_map.
        Call whenever:
          - the item is first created
          - after an enchantment
          - when the owner’s level changes
        """
        # Clear existing maps
        self.bonuses.clear()
        self.damage_map.clear()

        # 1) Scale base bonuses
        for stat_name, rng_dict in self.base_bonus_ranges.items():
            lo = int(rng_dict.get("min", 0))
            hi = int(rng_dict.get("max", lo))
            # Pass a (lo, hi) tuple to scale_stat, not a dict
            rolled = scale_stat((lo, hi), current_level, self.grade, self.rarity)
            self.bonuses[stat_name] = rolled

        # 2) Scale raw_damage_map → damage_map
        # First roll each damage type from its range, then call scale_damage_map
        rolled_damage: Dict[str, int] = {}
        for dt_str, rng_dict in self.raw_damage_map.items():
            lo = int(rng_dict.get("min", 0))
            hi = int(rng_dict.get("max", lo))
            rolled_amount = random.randint(lo, hi)
            rolled_damage[dt_str.upper()] = rolled_amount

        scaled = scale_damage_map(rolled_damage, current_level, self.grade, self.rarity)
        final_map: Dict[DamageType, int] = {}
        for dt_str, amt in scaled.items():
            try:
                dt_enum = DamageType[dt_str.upper()]
                final_map[dt_enum] = amt
            except Exception:
                # Skip unknown damage types
                continue
        self.damage_map = final_map

        # 3) Apply percent bonuses on top of numeric bonuses
        for stat_name, pct in self.percent_bonuses.items():
            if stat_name in self.bonuses:
                self.bonuses[stat_name] = int(round(self.bonuses[stat_name] * (1.0 + pct / 100.0)))
            else:
                # If stat wasn't in bonuses, initialize to 0
                self.bonuses[stat_name] = 0

    def apply_passives_to(self, owner: "Actor", combat_engine) -> None:
        """
        When equipped, convert each JSON dict in self.passive_Effects into an Effect
        and add it to owner.effects.
        """
        from game_sys.effects.base import Effect  # local import

        for eff_data in self.passive_Effects:
            try:
                eff_obj = Effect.from_dict(eff_data)
                owner.effects.add(eff_obj)
            except Exception:
                continue

    def remove_passives_from(self, owner: "Actor") -> None:
        """
        When unequipped, remove Effects that were added by this item.
        """
        from game_sys.effects.base import Effect  # local import

        to_remove: List["Effect"] = []
        for eff_data in self.passive_Effects:
            try:
                candidate = Effect.from_dict(eff_data)
                for active in owner.effects:
                    if type(active) is type(candidate) and active.__dict__ == candidate.__dict__:
                        to_remove.append(active)
                        break
            except Exception:
                continue

        for eff in to_remove:
            try:
                owner.effects.remove(eff)
            except ValueError:
                pass

    def __repr__(self):
        return (
            f"<EquipableItem id={self.id!r}, slot={self.slot!r}, "
            f"level={self.level.lvl}, grade={self.grade}, rarity={self.rarity.name}>"
        )


class ConsumableItem(Item):
    """
    A consumable that applies a sequence of Effects to the actor (self‐target).
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        price: int,
        level: int,
        effects_data: List[Dict[str, Any]],
    ):
        super().__init__(id, name, description, price, level)
        from game_sys.effects.base import Effect  # local import

        self.effects: List["Effect"] = []
        for e_data in effects_data:
            try:
                self.effects.append(Effect.from_dict(e_data))
            except Exception:
                continue

    def apply(self, actor: "Actor", combat_engine) -> str:
        """
        Apply each Effect in self.effects to the target (actor). Return a newline‐joined log.
        """
        log_parts: List[str] = []
        for eff in self.effects:
            try:
                msg = eff.apply(actor, actor, combat_engine)
                log_parts.append(msg)
            except Exception as e:
                log_parts.append(f"[Error applying effect {type(e).__name__}: {e}]")
        return "\n".join(log_parts)

    def __repr__(self):
        return f"<ConsumableItem id={self.id!r}, level={self.level.lvl}, effects={len(self.effects)}>"

    # Alias so legacy code expecting “Equipable” continues to work
    Equipable = EquipableItem
