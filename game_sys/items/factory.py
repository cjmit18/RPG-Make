# game_sys/items/factory.py

import random
from typing import Dict, Any
from pathlib import Path
from .item_base import Equipable, Item
from .consumable_list import Consumable

# Load raw JSON templates (item_id -> template dict)
from .loader import load_templates
_TEMPLATES: Dict[str, Any] = load_templates()


def _roll_field(spec: Any, rng: Any = random) -> Any:
    """
    If spec is a dict with 'min' and 'max', roll an int in [min, max].
    Otherwise, return spec unchanged.
    """
    if isinstance(spec, dict) and "min" in spec and "max" in spec:
        return rng.randint(spec["min"], spec["max"])
    return spec


def _instantiate(template: Dict[str, Any], rng: Any = random) -> Item:
    """
    Given a JSON template, return a new Item, Equipable, or Consumable.
    Expects keys: id, type, name, description, price, level, etc.
    """
    item_type = template["type"]
    item_id = template["id"]
    name = template["name"]
    description = template.get("description", "")
    price = int(template.get("price", 0))
    level = int(template.get("level", 1))

    if item_type == "consumable":
        eff = template["effect"][0]
        stat_name = eff["stat_name"]

        amount_spec = eff["amount"]
        amount = rng.randint(amount_spec["min"], amount_spec["max"]) \
                 if isinstance(amount_spec, dict) else int(amount_spec)

        duration = int(eff.get("duration", 0))

        obj = Consumable(
            name=name,
            description=description,
            price=price,
            level=level,
            effect=stat_name,
            amount=amount,
            duration=duration,
        )
        obj.id = item_id
        return obj

    elif item_type in ("equipment", "equipable"):
        slot = template["slot"]
        raw_bonuses: Dict[str, Any] = template.get("bonuses", {})
        bonuses: Dict[str, int] = {}
        for stat, spec in raw_bonuses.items():
            rolled = _roll_field(spec, rng)
            bonuses[stat] = int(rolled)
        obj = Equipable(
            name=name,
            description=description,
            price=price,
            level=level,
            slot=slot,
            bonuses=bonuses,
        )
        obj.id = item_id

        obj.offhand = bool(template.get("offhand", False))
        return obj

    else:
        # Generic Item
        obj = Item(name=name, description=description, price=price, level=level)
        obj.id = item_id
        return obj


def create_item(item_id: str, rng: Any = random) -> Item:
    """
    Public factory: Looks up the template by ID and instantiates a new Item.
    """
    template = _TEMPLATES.get(item_id)
    if template is None:
        raise KeyError(f"No item template for id={item_id!r}")

    import copy
    templ_copy = copy.deepcopy(template)
    return _instantiate(templ_copy, rng)


def list_all_ids() -> list[str]:
    """Return a list of all defined item IDs."""
    return list(_TEMPLATES.keys())
