# game_sys/items/factory.py
import copy
import random
from typing import Dict, Any
from .loader import load_templates
from .item_base import Equipable, Item
from .consumable_list import Consumable

# Load raw templates once
_TEMPLATES: Dict[str, Any] = load_templates()

def _roll_field(spec: Any, rng: Any = random) -> Any:
    """
    If spec is a dict with "min" and "max", roll an int in that range.
    Otherwise, return the spec unchanged.
    """
    if isinstance(spec, dict) and "min" in spec and "max" in spec:
        return rng.randint(spec["min"], spec["max"])
    return spec


def _instantiate(template: Dict[str, Any], rng: Any = random) -> Item:
    """
    Create a fresh Item/Equipable/Consumable from a template,
    rolling any ranged fields.
    """
    data = copy.deepcopy(template)
    item_id = data.pop("id", None)
    kind = data.pop("type", None)

    # Roll ranged bonuses for equipment
    if kind == "equipment" and "bonuses" in data:
        data["bonuses"] = {
            stat: _roll_field(val, rng)
            for stat, val in data["bonuses"].items()
        }

    # Roll ranged amount for consumables
    if kind == "consumable" and "amount" in data:
        data["amount"] = _roll_field(data["amount"], rng)

    if kind == "consumable":
        item = Consumable(**data)
    else:
        item = Equipable(**data)

    # Ensure each item has an "id" attribute
    if item_id is not None:
        setattr(item, "id", item_id)
    return item


def create_item(item_id: str, rng: Any = random) -> Item:
    """
    Public factory: looks up the template by ID,
    instantiates a new Item with rolled stats.
    """
    template = _TEMPLATES.get(item_id)
    if template is None:
        raise KeyError(f"No item template for id={item_id!r}")
    return _instantiate(template, rng)


def list_all_ids() -> list[str]:
    """Return a list of all defined item IDs."""
    return list(_TEMPLATES.keys())
