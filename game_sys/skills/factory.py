# game_sys/skills/factory.py

import json
from pathlib import Path
from typing import Dict, Any
from game_sys.skills.registry import SkillRegistry

# load JSON once
_DATA: Dict[str, Dict[str, Any]] = {}
_path = Path(__file__).parent / "data" / "skills.json"
if _path.exists():
    _DATA = json.loads(_path.read_text()).get("skills", {})


class SkillFactory:
    """
    Builds Skill instances from JSON definitions.
    """

    @staticmethod
    def create(skill_id: str):
        data = _DATA.get(skill_id, {})
        # pick the base class or a subclass from registry
        cls = SkillRegistry.get(skill_id)
        return cls(
            skill_id=skill_id,
            name=data.get("name", skill_id),
            stamina_cost=data.get("stamina_cost", 0.0),
            cooldown=data.get("cooldown", 0.0),
            base_power=data.get("base_power", 0.0),
            damage_type=data.get("damage_type", "PHYSICAL"),
            effect_defs=data.get("effects", [])
        )
