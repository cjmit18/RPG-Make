# game_sys/enchantments/factory.py

import os
import json
from typing import Dict
from .base import Enchantment

_THIS_DIR = os.path.dirname(__file__)
_JSON_PATH = os.path.join(_THIS_DIR, "data", "enchantments.json")

# Load once at import time
try:
    with open(_JSON_PATH, "r", encoding="utf-8") as f:
        _raw_list = json.load(f)
except FileNotFoundError:
    _raw_list = []

_ENCHANTMENTS: Dict[str, Enchantment] = {}
for entry in _raw_list:
    try:
        obj = Enchantment.from_dict(entry)
    except Exception:
        continue
    _ENCHANTMENTS[obj.enchant_id] = obj


def create_enchantment(enchant_id: str) -> Enchantment:
    """
    Given an enchant_id, return a new Enchantment instance.
    Raises KeyError if not found.
    """
    if enchant_id not in _ENCHANTMENTS:
        raise KeyError(f"Enchantment '{enchant_id}' not found.")
    # Return a shallow copy (so caller cannot mutate the template directly)
    base = _ENCHANTMENTS[enchant_id]
    return Enchantment(
        enchant_id=base.enchant_id,
        name=base.name,
        description=base.description,
        bonus_ranges=base.bonus_ranges.copy(),
        applicable_slots=list(base.applicable_slots),
        level_requirement=base.level_requirement,
        rarity=base.rarity,
    )


def list_all_enchantments() -> Dict[str, Enchantment]:
    """
    Return the mapping of all loaded enchant_id → Enchantment template.
    """
    return dict(_ENCHANTMENTS)
