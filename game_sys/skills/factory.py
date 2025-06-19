# file: game_sys/skills/factory.py

import os
import json
import copy
import random
from typing import Dict, Any, List, Optional
from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.core.rarity import Rarity
from game_sys.managers.scaling_manager import scale_damage_map, _GRADE_STATS_MULTIPLIER as _GRADE_MODIFIERS
from game_sys.effects.base import Effect
from game_sys.skills.base import Skill
log = get_logger(__name__)

# Load skill templates from JSON
_THIS_DIR = os.path.dirname(__file__)
_SKILLS_JSON_PATH = os.path.join(_THIS_DIR, "data", "skills.json")
with open(_SKILLS_JSON_PATH, "r", encoding="utf-8") as f:
    _skills_list: List[Dict[str, Any]] = json.load(f)

# Map skill_id → template dict
_skill_defs: Dict[str, Dict[str, Any]] = {
    t["skill_id"]: t for t in _skills_list
}


# Grade-based multiplier modifiers
def create_skill(
    skill_id: str,
    level: Optional[int] = None,
    grade: int = 1,
    rarity: Rarity = Rarity.COMMON,
    seed: Optional[int] = None,
    rng: Optional[random.Random] = None
) -> Skill:
    """
    Instantiate a Skill with optional scaling:
    - `level`, `grade`, and `rarity` determine damage scaling.
    - `seed` or `rng` for reproducible randomness in variable damage.
    """
    # Determine RNG
    if rng is None:
        rng = random.Random(seed) if seed is not None else random.Random()

    template = _skill_defs.get(skill_id)
    if template is None:
        raise KeyError(f"Skill ID '{skill_id}' not found in skills.json.")

    # Deep copy to avoid mutating original
    templ_copy = copy.deepcopy(template)

    # Process and scale effects
    effect_objs: List[Effect] = []
    for eff_data in templ_copy.get("effects", []):
        eff_copy = eff_data.copy()
        if eff_copy.get("type") == "Damage" and level is not None:
            raw_damage_spec = eff_copy.get("damage", {})
            # Convert and roll raw damage per type
            raw_dtype_map: Dict[DamageType, int] = {}
            for dt_str, spec in raw_damage_spec.items():
                dt = DamageType[dt_str.upper()]
                if isinstance(spec, dict):
                    lo = int(spec.get("min", 0))
                    hi = int(spec.get("max", lo))
                    val = rng.randint(lo, hi) if hi >= lo else lo
                else:
                    val = int(spec)
                raw_dtype_map[dt] = val

            # Scale by level, grade, rarity
            scaled_map = scale_damage_map(
                raw_dtype_map,
                level,
                grade=grade,
                rarity=rarity
            )
            # Apply grade modifier
            for dt, dmg in scaled_map.items():
                scaled_map[dt] = int(dmg * _GRADE_MODIFIERS.get(grade, 1.0))

            # Write back scaled damage to effect
            eff_copy["damage"] = {
                dt.name: dmg
                for dt, dmg in scaled_map.items()
            }

        # Instantiate the Effect
        effect_objs.append(Effect.from_dict(eff_copy))

    # Build and return Skill
    return Skill(
        skill_id=templ_copy["skill_id"],
        name=templ_copy.get("name", ""),
        description=templ_copy.get("description", ""),
        mana_cost=int(templ_copy.get("mana_cost", 0)),
        stamina_cost=int(templ_copy.get("stamina_cost", 0)),
        cooldown=int(templ_copy.get("cooldown", 0)),
        effects=effect_objs,
        requirements=templ_copy.get("requirements", {}) or {},
    )
