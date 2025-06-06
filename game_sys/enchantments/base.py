# game_sys/enchantments/base.py

import json
from pathlib import Path
from typing import Dict, Any, List
from game_sys.items.rarity import Rarity

class Enchantment:
    """
    Represents a single enchantment template. JSON schema example:

    [
      {
        "enchant_id": "flamebrand",
        "name": "Flamebrand",
        "description": "Adds extra Fire damage.",
        "bonus_ranges": {
          "damage_map": {
            "FIRE": {"min": 2, "max": 5}
          },
          "percent_bonuses": {
            "physical": 10,
            "attack_speed": 5
          }
        },
        "applicable_slots": ["weapon"],
        "level_requirement": 1,
        "rarity": "RARE"
      }
    ]
    """

    def __init__(
        self,
        enchant_id: str,
        name: str,
        description: str,
        bonus_ranges: Dict[str, Any],
        applicable_slots: List[str],
        level_requirement: int,
        rarity: Rarity,
    ):
        self.enchant_id: str = enchant_id
        self.name: str = name
        self.description: str = description
        # e.g.:
        #   { "damage_map": { "FIRE": {"min":2,"max":5} },
        #     "percent_bonuses": { "physical": 10, "attack_speed": 5 } }
        self.bonus_ranges: Dict[str, Any] = bonus_ranges
        self.applicable_slots: List[str] = applicable_slots
        self.level_requirement: int = level_requirement
        self.rarity: Rarity = rarity

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Enchantment":
        """
        Instantiate an Enchantment from a JSON‐style dict. Expects keys:
          - "enchant_id": str
          - "name": str
          - "description": str
          - "bonus_ranges": dict (see docstring)
          - "applicable_slots": list[str]
          - "level_requirement": int
          - "rarity": str (e.g. "COMMON", "RARE", etc.)
        """
        eid = data.get("enchant_id")
        if not isinstance(eid, str):
            raise ValueError(f"Enchantment requires string 'enchant_id', got {eid!r}")

        name = data.get("name", "")
        desc = data.get("description", "")
        branges = data.get("bonus_ranges", {})
        if not isinstance(branges, dict):
            raise ValueError(f"'bonus_ranges' must be a dict for enchant '{eid}'")

        slots = data.get("applicable_slots", [])
        if not isinstance(slots, list) or not all(isinstance(s, str) for s in slots):
            raise ValueError(f"'applicable_slots' must be a list of strings for enchant '{eid}'")

        lvl_req = data.get("level_requirement", 1)
        if not isinstance(lvl_req, int):
            raise ValueError(f"'level_requirement' must be int for enchant '{eid}', got {lvl_req!r}")

        rarity_str = data.get("rarity", "COMMON").upper()
        try:
            rarity_enum = Rarity[rarity_str]
        except KeyError:
            raise ValueError(f"Unknown rarity '{rarity_str}' for enchant '{eid}'")

        return cls(
            enchant_id=eid,
            name=name,
            description=desc,
            bonus_ranges=branges,
            applicable_slots=slots,
            level_requirement=lvl_req,
            rarity=rarity_enum,
        )

    @classmethod
    def load_all(cls, path: Path) -> Dict[str, "Enchantment"]:
        """
        Load a JSON array of enchantment definitions from 'path',
        returning a dict: { enchant_id → Enchantment(...) }.
        """
        try:
            text = path.read_text(encoding="utf-8")
            raw_list = json.loads(text)
        except Exception as e:
            print(f"[Warning] Could not load enchantments JSON at {path}: {e}")
            return {}

        result: Dict[str, Enchantment] = {}
        for entry in raw_list:
            try:
                ench = cls.from_dict(entry)
            except Exception as exc:
                print(f"[Warning] Skipping invalid enchantment entry: {exc}")
                continue
            result[ench.enchant_id] = ench
        return result
