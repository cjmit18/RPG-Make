# game_sys/skills/skills.py

import json
import os
from typing import Dict, Any, List, Union
from game_sys.effects.base import Effect
from game_sys.skills.base import Skill

_THIS_DIR = os.path.dirname(__file__)
_SKILLS_JSON_PATH = os.path.join(_THIS_DIR, "data", "skills.json")

with open(_SKILLS_JSON_PATH, "r", encoding="utf-8") as f:
    _skills_list: List[Dict[str, Any]] = json.load(f)

_skill_defs: Dict[str, Dict[str, Any]] = {
    entry["skill_id"]: entry for entry in _skills_list
}


def create_skill(skill_id: str) -> Skill:
    """
    Instantiate a Skill, converting each JSON “effects” entry
    into an Effect object via Effect.from_dict(...).
    """
    template = _skill_defs.get(skill_id)
    if not template:
        raise KeyError(f"Skill ID '{skill_id}' not found in skills.json.")

    # (1) Parse each effect JSON dict into an Effect instance
    effect_objs: List[Effect] = []
    for eff_data in template.get("effects", []):
        effect_objs.append(Effect.from_dict(eff_data))

    # (2) Create the Skill, passing the list of Effect objects
    new_skill = Skill(
        skill_id=template["skill_id"],
        name=template["name"],
        description=template.get("description", ""),
        mana_cost=template.get("mana_cost", 0),
        stamina_cost=template.get("stamina_cost", 0),
        cooldown=template.get("cooldown", 0),
        effects=effect_objs,
    )

    return new_skill
