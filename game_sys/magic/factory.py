# game_sys/magic/factory.py

import json
from pathlib import Path
from typing import Dict, Any
from game_sys.magic.registry import SpellRegistry
from game_sys.logging import magic_logger, log_exception

_DATA: Dict[str, Dict[str, Any]] = {}
_path = Path(__file__).parent / "data" / "spells.json"
if _path.exists():
    try:
        _DATA = json.loads(_path.read_text()).get("spells", {})
        magic_logger.info(f"Loaded {len(_DATA)} spells from {_path}")
    except Exception as e:
        magic_logger.error(f"Failed to load spells from {_path}: {e}")
else:
    magic_logger.warning(f"Spells data file not found: {_path}")


class SpellFactory:
    """
    Builds Spell instances from JSON definitions.
    """
    @staticmethod
    @log_exception
    def create(spell_id: str):
        magic_logger.debug(f"Creating spell with ID: {spell_id}")
        
        data = _DATA.get(spell_id, {})
        if not data:
            magic_logger.warning(f"No data found for spell: {spell_id}")
            
        cls = SpellRegistry.get(spell_id)
        
        spell = cls(
            spell_id=spell_id,
            name=data.get("name", spell_id),
            mana_cost=data.get("mana_cost", 0.0),
            cast_time=data.get("cast_time", 0.0),
            cooldown=data.get("cooldown", 0.0),
            base_power=data.get("base_power", 0.0),
            damage_type=data.get("damage_type", "MAGIC"),
            effect_defs=data.get("effects", []),
            shape_def=data.get("shape"),
            target_group=data.get("target_group", "target")
        )
        
        magic_logger.info(
            f"Created spell: {spell.name} ({spell_id}) with "
            f"{len(data.get('effects', []))} effects"
        )
        return spell
