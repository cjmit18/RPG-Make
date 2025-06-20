# game_sys/items/factory.py

import random
from typing import Dict, Any, List, Optional, Union
from .item_base import Item, EquipableItem, ConsumableItem
from .loader import load_templates
from game_sys.core.rarity import Rarity
from game_sys.managers.scaling_manager import (
    scale_stat,
    scale_damage_map,
    roll_item_rarity,
    roll_weighted_value,
)
from game_sys.core.damage_types import DamageType
from game_sys.enchantments.base import BasicEnchantment
from game_sys.hooks.hooks import hook_dispatcher

# Load templates once at import time
_TEMPLATES: Dict[str, Dict[str, Any]] = {
    tpl["id"]: tpl for tpl in load_templates()
    if isinstance(tpl, dict) and "id" in tpl
}


def _roll_field(spec: Any, rng: random.Random) -> Any:
    """
    Supports int/float/raw dict ranges/lists:
      - numbers and strings return as-is
      - {"min": x, "max": y} → random int between x and y
      - [a, b, c]     → choose one entry (and recurse)
    """
    if isinstance(spec, (int, float, str, bool)):
        return spec
    if isinstance(spec, dict):
        lo = spec.get("min")
        hi = spec.get("max", lo)
        if lo is None:
            raise ValueError(f"Invalid range spec without 'min': {spec!r}")
        return rng.randint(int(lo), int(hi))
    if isinstance(spec, list) and spec:
        return _roll_field(rng.choice(spec), rng)
    return spec


def _instantiate(
    templ: Dict[str, Any],
    rng: random.Random,
    roll_level: bool = False,
    roll_grade: bool = False,
    roll_rarity: bool = False,
) -> Item:
    # Common fields
    item_type = templ.get("type", "").lower()
    item_id   = templ.get("id", "<unknown>")
    name      = templ.get("name", item_id)
    desc      = templ.get("description", "")
    base_lvl  = int(templ.get("level", 1))
    base_grd  = int(templ.get("grade", 1))
    raw_rarity= templ.get("rarity", "COMMON")

    # Roll or use direct
    level = roll_weighted_value(base_lvl, rng)  if roll_level else base_lvl
    grade = roll_weighted_value(base_grd, rng)  if roll_grade else base_grd

    # Rarity
    if "__explicit_rarity__" in templ:
        rr = templ["__explicit_rarity__"]
        rarity = rr if isinstance(rr, Rarity) else Rarity[rr.upper()]
    elif roll_rarity:
        rarity = roll_item_rarity(Rarity[raw_rarity.upper()], rng)
    else:
        rarity = Rarity[raw_rarity.upper()] if isinstance(raw_rarity, str) else raw_rarity

    # Price scaling
    price = scale_stat(int(templ.get("price", 0)), level, grade, rarity)

    # Parse resistances (both singular & plural keys)
    resist_src = templ.get("resistances", templ.get("resistance", {})) or {}
    resistances: Dict[DamageType, float] = {}
    for k, v in resist_src.items():
        try:
            dt = DamageType[k.upper()]
            resistances[dt] = float(v)
        except Exception:
            continue

    # Build item
    if item_type == "equipable":
        # stat bonuses
        bbr = templ.get("base_bonus_ranges", {})
        base_bonus_ranges = {
            stat: {
                "min": scale_stat((spec.get("min",0), spec.get("max",0)), level, grade, rarity),
                "max": scale_stat((spec.get("min",0), spec.get("max",0)), level, grade, rarity),
            }
            for stat, spec in bbr.items()
        }

        # raw damage → scaled damage_map
        raw_map = {}
        for k, spec in templ.get("raw_damage_map", {}).items():
            if k.upper() in DamageType.__members__:
                dmg_amt = _roll_field(spec, rng)
                raw_map[ DamageType[k.upper()] ] = int(dmg_amt)
        dmg_map = scale_damage_map(raw_map, level, grade, rarity)

        percent_bonuses = {stat: float(pct) for stat, pct in templ.get("percent_bonuses", {}).items()}
        passive_effects = templ.get("passive_effects", []) or []
        enchantments = [ BasicEnchantment.from_dict(e) for e in templ.get("enchantments", []) ]

        return EquipableItem(
            id=item_id,
            name=name,
            description=desc,
            price=price,
            level=level,
            slot=templ.get("slot",""),
            grade=grade,
            rarity=rarity,
            base_bonus_ranges=base_bonus_ranges,
            damage_map={ dt.name: {"min": amt, "max": amt} for dt, amt in dmg_map.items() },
            percent_bonuses=percent_bonuses,
            passive_effects=passive_effects,
            enchantments=enchantments,
            resistances=resistances,
        )

    elif item_type == "consumable":
        effs = templ.get("effects", [])
        effects_data: List[Dict[str,Any]] = []
        for eff in effs:
            e = dict(eff)
            if isinstance(e.get("amount"), dict):
                e["amount"] = _roll_field(e["amount"], rng)
            effects_data.append(e)
        amt = int(_roll_field(templ.get("amount",1), rng))

        return ConsumableItem(
            id=item_id,
            name=name,
            description=desc,
            price=price,
            level=level,
            effects_data=effects_data,
            amount=amt,
            grade=grade,
            rarity=rarity,
        )

    else:
        # fallback generic
        return Item(
            id=item_id,
            name=name,
            description=desc,
            price=price,
            level=level,
            grade=grade,
            rarity=rarity,
        )


def create_item(
    item_id: str,
    rng: Optional[random.Random] = None,
    seed: Optional[int] = None,
    level: Optional[int] = None,
    grade: Optional[int] = None,
    rarity: Optional[Union[Rarity,str]] = None,
    roll_level: bool = False,
    roll_grade: bool = False,
    roll_rarity: bool = False,
) -> Item:
    rng = random.Random(seed) if seed is not None else random.Random()
    import copy
    templ = copy.deepcopy(_TEMPLATES.get(item_id, {}))
    if not templ:
        raise KeyError(f"No template for item_id={item_id!r}")
    if level  is not None: templ["level"]  = level
    if grade  is not None: templ["grade"]  = grade
    if rarity is not None: templ["__explicit_rarity__"] = rarity
    hook_dispatcher.fire("item.created", item=templ, seed=seed, rng=rng)
    return _instantiate(templ, rng, roll_level, roll_grade, roll_rarity)


def list_all_ids() -> List[str]:
    return list(_TEMPLATES.keys())
