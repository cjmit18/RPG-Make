import random
from typing import Dict, Any, List, Optional

from .item_base import Item, EquipableItem, ConsumableItem
from .loader import load_templates
from game_sys.items.rarity import Rarity

# Load all item templates at module‐import time
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

        # Build base bonus ranges: {stat: {"min": X, "max": Y}}
        base_bonus_ranges: Dict[str, Dict[str, int]] = {}
        for stat, rng_spec in template.get("base_bonus_ranges", {}).items():
            lo = int(rng_spec.get("min", 0))
            hi = int(rng_spec.get("max", lo))
            base_bonus_ranges[stat] = {"min": lo, "max": hi}

        # Build raw damage map: {type: {"min": X, "max": Y}}
        raw_damage_map: Dict[str, Dict[str, int]] = {}
        for dt_str, rng_spec in template.get("raw_damage_map", {}).items():
            lo = int(rng_spec.get("min", 0))
            hi = int(rng_spec.get("max", lo))
            raw_damage_map[dt_str.upper()] = {"min": lo, "max": hi}

        is_enchantable = bool(template.get("is_enchantable", False))

        # Optional percent bonuses
        percent_bonuses: Dict[str, float] = {}
        for stat, pct in template.get("percent_bonuses", {}).items():
            percent_bonuses[stat] = float(pct)

        # Optional passive effects
        passive_effects_list = template.get("passive_Effects", [])
        if not isinstance(passive_effects_list, list):
            raise ValueError(f"'passive_Effects' must be a list for item '{item_id}'")
        passive_effects_copy: List[Dict[str, Any]] = [eff.copy() for eff in passive_effects_list]

        item = EquipableItem(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            slot=slot,
            grade=grade,
            rarity=rarity,
            base_bonus_ranges=base_bonus_ranges,
            raw_damage_map=raw_damage_map,
            is_enchantable=is_enchantable,
            percent_bonuses=percent_bonuses,
            passive_Effects=passive_effects_copy,
        )

        # Immediately scale at the item’s own level
        item.rescale(current_level=level)
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
