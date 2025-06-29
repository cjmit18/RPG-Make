# game_sys/magic/factory.py

import json
from pathlib import Path
from typing import Dict, Any
from game_sys.magic.registry import SpellRegistry

_DATA: Dict[str, Dict[str, Any]] = {}
_path = Path(__file__).parent / "data" / "spells.json"
if _path.exists():
    _DATA = json.loads(_path.read_text()).get("spells", {})


class SpellFactory:
    """
    Builds Spell instances from JSON definitions.
    """
    @staticmethod
    def create(spell_id: str):
        data = _DATA.get(spell_id, {})
        cls = SpellRegistry.get(spell_id)
        return cls(
            spell_id=spell_id,
            name=data.get("name", spell_id),
            mana_cost=data.get("mana_cost", 0.0),
            cast_time=data.get("cast_time", 0.0),
            cooldown=data.get("cooldown", 0.0),
            base_power=data.get("base_power", 0.0),
            damage_type=data.get("damage_type", "MAGIC"),
            effect_defs=data.get("effects", [])
        )
