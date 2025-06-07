# File: game_sys/items/factory.py

import random
from typing import Dict, Any, List, Optional

from .item_base import Item, EquipableItem, ConsumableItem
from .loader import load_templates
from game_sys.items.rarity import Rarity
from game_sys.items.scaler import scale_stat, scale_damage_map
from game_sys.core.damage_types import DamageType

# Load all item templates at module-import time
_TEMPLATES: Dict[str, Any] = load_templates()


def _roll_field(spec: Any, rng: random.Random = random) -> Any:
    """
    If spec is a dict with 'min' and 'max', return a random int in [min, max].
    Otherwise, return spec unchanged.
    """
    if isinstance(spec, dict) and "min" in spec and "max" in spec:
        lo = int(spec["min"])
        hi = int(spec["max"])
        return rng.randint(lo, hi) if hi >= lo else lo
    return spec


def _instantiate(template: Dict[str, Any], rng: random.Random) -> Item:
    """
    Given a deep‐copied template dict from JSON, build either:
      - EquipableItem (for type="equipable")
      - ConsumableItem (for type="consumable")
    We now supply 'grade' and 'rarity' to scale_stat(...) calls, and pass
    raw_damage_map (dtype→int) directly to scale_damage_map.
    """
    item_type = template.get("type")
    item_id = template.get("id")
    name = template.get("name", "")
    description = template.get("description", "")
    price = int(template.get("price", 0))
    level = int(template.get("level", 1))

    if item_type == "equipable":
        slot = template["slot"]
        grade = int(template.get("grade", 1))
        rarity_str = template.get("rarity", "COMMON").upper()
        try:
            rarity = Rarity[rarity_str]
        except KeyError:
            raise ValueError(f"Unknown rarity '{rarity_str}' for item '{item_id}'")

        # 1) Build and SCALE base bonus values: pick a single scaled int from the range
        scaled_bonus_ranges: Dict[str, Dict[str, int]] = {}
        for stat, rng_spec in template.get("base_bonus_ranges", {}).items():
            raw_lo = int(rng_spec.get("min", 0))
            raw_hi = int(rng_spec.get("max", raw_lo))
            # Pass a tuple (raw_lo, raw_hi) to scale_stat
            scaled_val = scale_stat(
                (raw_lo, raw_hi), level, grade=grade, rarity=rarity
            )
            # Use the same scaled_val for both "min" and "max"
            scaled_bonus_ranges[stat] = {"min": scaled_val, "max": scaled_val}

        # 2) Build raw damage map: {DamageType: base_int}
        raw_damage_map: Dict[DamageType, int] = {}
        for dt_str, rng_spec in template.get("raw_damage_map", {}).items():
            raw_lo = int(rng_spec.get("min", 0))
            raw_hi = int(rng_spec.get("max", raw_lo))
            # Pick raw_lo as the “base” for scaling
            raw_damage_map[DamageType[dt_str.upper()]] = raw_lo

        # 3) Call scale_damage_map with raw_damage_map (dtype→int)
        scaled_damage_map: Dict[DamageType, int] = scale_damage_map(
            raw_damage_map, level, grade=grade, rarity=rarity
        )

        is_enchantable = bool(template.get("is_enchantable", False))

        # Optional percent bonuses (already percentages)
        percent_bonuses: Dict[str, float] = {}
        for stat, pct in template.get("percent_bonuses", {}).items():
            percent_bonuses[stat] = float(pct)

        # Optional passive effects
        passive_effects_list = template.get("passive_Effects", [])
        if not isinstance(passive_effects_list, list):
            raise ValueError(f"'passive_Effects' must be a list for item '{item_id}'")
        passive_effects_copy: List[Dict[str, Any]] = [eff.copy() for eff in passive_effects_list]

        # 4) Construct the EquipableItem with already-scaled values
        item = EquipableItem(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            slot=slot,
            grade=grade,
            rarity=rarity,
            base_bonus_ranges=scaled_bonus_ranges,
            raw_damage_map={dt.name: {"min": dmg, "max": dmg} for dt, dmg in scaled_damage_map.items()},
            is_enchantable=is_enchantable,
            percent_bonuses=percent_bonuses,
            passive_Effects=passive_effects_copy,
        )

        return item

    elif item_type == "consumable":
        effects_data = template.get("effects", [])
        if not isinstance(effects_data, list):
            raise ValueError(f"'effects' must be a list for consumable '{item_id}'")
        return ConsumableItem(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            effects_data=effects_data,
        )

    else:
        raise KeyError(f"Unknown item type '{item_type}' for id '{item_id}'")


def create_item(item_id: str, rng: Optional[random.Random] = None) -> Item:
    """
    Public factory function. Returns a fresh Item (EquipableItem or ConsumableItem)
    based on the JSON template for 'item_id'. Raises KeyError if no template found.
    """
    rng = rng or random.Random()

    template = _TEMPLATES.get(item_id)
    if template is None:
        raise KeyError(f"No item template for id={item_id!r}")

    import copy
    templ_copy = copy.deepcopy(template)
    return _instantiate(templ_copy, rng)


def list_all_ids() -> List[str]:
    """Return a list of all defined item IDs."""
    return list(_TEMPLATES.keys())
