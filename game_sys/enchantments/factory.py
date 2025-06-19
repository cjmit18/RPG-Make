# game_sys/enchantments/factory.py

import random
from pathlib import Path
from typing import Optional, Dict, Any
from game_sys.enchantments.base import BasicEnchantment
from game_sys.core.rarity import Rarity
from game_sys.core.damage_types import DamageType
from game_sys.managers.scaling_manager import scale_stat

# Load raw enchantment templates at import
_TEMPLATES: Dict[str, Dict[str, Any]] = BasicEnchantment.load_all(Path(__file__).parent)


def create_enchantment(
    enchant_id: str,
    level: Optional[int] = None,
    grade: Optional[int] = None,
    rarity: Optional[Rarity] = None,
    seed: Optional[int] = None,
    rng: Optional[random.Random] = None
) -> BasicEnchantment:
    """
    Create a BasicEnchantment scaled by level, grade, and rarity.
    Uses fallback to JSON template values if level/grade/rarity is not passed.
    """
    if rng is None:
        rng = random.Random(seed) if seed is not None else random.Random()

    templ = _TEMPLATES.get(enchant_id)
    if templ is None:
        raise KeyError(f"No enchantment template for id='{enchant_id}'")

    # Resolve level
    lvl = int(level) if level is not None else int(templ.get("level", 1))
    # Resolve grade
    grd = int(grade) if grade is not None else int(templ.get("grade", 1))
    # Resolve rarity
    rar_str = (
        rarity.name if isinstance(rarity, Rarity)
        else str(rarity or templ.get("rarity", "COMMON"))
    ).upper()
    rar = Rarity[rar_str] if rar_str in Rarity.__members__ else Rarity.COMMON

    # Roll stat bonuses using scale_stat
    stat_bonuses: Dict[str, int] = {}
    for stat, spec in templ.get("stat_bonuses", {}).items():
        base_range = (spec.get("min", 0), spec.get("max", 0))
        stat_bonuses[stat] = max(1, scale_stat(base_range, lvl, grd, rar))

    # Roll damage modifiers using scale_stat
    dmg_mods: Dict[DamageType, int] = {}
    for dt_str, spec in templ.get("damage_modifiers", {}).items():
        try:
            dt = DamageType[dt_str.upper()]
            base_range = (spec.get("min", 0), spec.get("max", 0))
            dmg_mods[dt] = max(0, scale_stat(base_range, lvl, grd, rar))
        except KeyError:
            continue

    return BasicEnchantment(
        enchant_id=enchant_id,
        name=templ.get("name", enchant_id),
        description=templ.get("description", ""),
        level=lvl,
        grade=grd,
        rarity=rar,
        applicable_slots=templ.get("applicable_slots", []),
        stat_bonuses=stat_bonuses,
        damage_modifiers=dmg_mods,
    )
