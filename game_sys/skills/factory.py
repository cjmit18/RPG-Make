# game_sys/skills/skills.py

import json
import os
from typing import Dict, Any, List, Optional
from game_sys.items.scaler import scale_damage_map
from game_sys.core.damage_types import DamageType
from game_sys.effects.base import Effect
from game_sys.skills.base import Skill

_THIS_DIR = os.path.dirname(__file__)
_SKILLS_JSON_PATH = os.path.join(_THIS_DIR, "data", "skills.json")

with open(_SKILLS_JSON_PATH, "r", encoding="utf-8") as f:
    _skills_list: List[Dict[str, Any]] = json.load(f)

_skill_defs: Dict[str, Dict[str, Any]] = {
    entry["skill_id"]: entry for entry in _skills_list
}


def create_skill(skill_id: str, level: Optional[int] = None) -> Skill:
    """
    Instantiate a Skill, converting each JSON “effects” entry
    into an Effect object via Effect.from_dict(...).
    If `level` is provided, also scale any `damage_map` in the JSON.
    """
    template = _skill_defs.get(skill_id)
    if not template:
        raise KeyError(f"Skill ID '{skill_id}' not found in skills.json.")

    # (A) Parse each effect JSON dict into an Effect instance
    effect_objs: List[Effect] = []
    for eff_data in template.get("effects", []):
        effect_objs.append(Effect.from_dict(eff_data))

    # (B) Parse and SCALE raw damage_map (if present)
    scaled_map: Dict[DamageType, int] = {}
    raw_map_json: Dict[str, Any] = template.get("damage_map", {}) or {}
    if raw_map_json and level is not None:
        # Convert JSON-keys (e.g. "FIRE") → DamageType enums, values → ints
        raw_dtype_map: Dict[DamageType, int] = {}
        for dt_str, amt in raw_map_json.items():
            try:
                dt_enum = DamageType[dt_str.upper()]
                raw_dtype_map[dt_enum] = int(amt)
            except KeyError:
                # unknown damage type in JSON; skip it
                continue
        # Now scale the entire map at once
        scaled_map = scale_damage_map(raw_dtype_map, level)

    # (C) Instantiate Skill, passing along scaled_map
    new_skill = Skill(
        skill_id=template["skill_id"],
        name=template["name"],
        description=template.get("description", ""),
        mana_cost=template.get("mana_cost", 0),
        stamina_cost=template.get("stamina_cost", 0),
        cooldown=template.get("cooldown", 0),
        damage_map=scaled_map,    # <— store the scaled values here
        effects=effect_objs,
        requirements=template.get("requirements", {}) or {},
    )

    return new_skill