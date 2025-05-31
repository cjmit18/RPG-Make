# game_sys/items/factory.py

import random
from typing import Dict, Any
from .loader import load_templates
from .item_base import Equipable, Item
from .consumable_list import Consumable

# Load raw JSON templates (item_id -> template dict)
_TEMPLATES: Dict[str, Any] = load_templates()

def _roll_field(spec: Any, rng: Any = random) -> Any:
    """
    If spec is a dict with "min" and "max", roll an int in [min, max].
    Otherwise, return spec unchanged.
    """
    if isinstance(spec, dict) and "min" in spec and "max" in spec:
        return rng.randint(spec["min"], spec["max"])
    return spec

def _instantiate(template: Dict[str, Any], rng: Any = random) -> Item:
    """
    Given a JSON template (with rolled fields), return a new Item or Equipable or Consumable.
    Expects template to have keys: id, type, name, description, price, level, etc.
    """
    item_type = template["type"]
    item_id = template["id"]
    name = template["name"]
    description = template.get("description", "")
    price = int(template.get("price", 0))
    level = int(template.get("level", 1))

    if item_type == "consumable":
        effect = template["effect"]
        # Roll amount if needed
        amount_spec = template["amount"]
        if isinstance(amount_spec, dict):
            amount = rng.randint(amount_spec["min"], amount_spec["max"])
        else:
            amount = int(amount_spec)
        duration = int(template.get("duration", 0))
        return Consumable(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            effect=effect,
            amount=amount,
            duration=duration
        )

    elif item_type in ("equipment", "equipable"):
        slot = template["slot"]
        # Bonuses may roll subfields; iterate over each stat
        raw_bonuses: Dict[str, Any] = template.get("bonuses", {})
        bonuses: Dict[str, int] = {}
        for stat, spec in raw_bonuses.items():
            rolled = _roll_field(spec, rng)
            bonuses[stat] = int(rolled)
        return Equipable(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level,
            slot=slot,
            bonuses=bonuses
        )

    else:
        # Generic Item or unknown type → return plain Item
        return Item(
            id=item_id,
            name=name,
            description=description,
            price=price,
            level=level
        )

def create_item(item_id: str, rng: Any = random) -> Item:
    """
    Public factory: Looks up the template by ID and instantiates a new Item (with rolled stats).
    """
    template = _TEMPLATES.get(item_id)
    if template is None:
        raise KeyError(f"No item template for id={item_id!r}")
    # Deep copy to avoid mutating the original then roll fields
    import copy
    templ_copy = copy.deepcopy(template)
    return _instantiate(templ_copy, rng)

def list_all_ids() -> list[str]:
    """Return a list of all defined item IDs."""
    return list(_TEMPLATES.keys())
