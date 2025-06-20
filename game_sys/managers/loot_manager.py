# game_sys/managers/loot_manager.py

from typing import Any, List
from game_sys.core.rarity import Rarity
from game_sys.items.factory import create_item
from game_sys.combat.loader import DROP_TABLES
import random

def get_enemy_key(enemy: Any) -> str:
    if hasattr(enemy, "job") and enemy.job:
        return enemy.job.job_id.lower()
    return type(enemy).__name__.lower()

def roll_loot(enemy: Any, rng: random.Random) -> List[Any]:
    items: List[Any] = []
    key = get_enemy_key(enemy)
    tiers = DROP_TABLES.get(key, [])
    lvl = getattr(enemy, "level", 1)
    grade = getattr(enemy, "grade", 1)

    tier = next(
        (t for t in tiers
         if t["min_level"] <= lvl <= t["max_level"]
            and t.get("min_grade", 0) <= grade <= t.get("max_grade", grade)),
        None
    )
    if not tier:
        return items

    for drop in tier["drops"]:
        if rng.random() <= drop.get("chance", 0):
            qty = rng.randint(drop.get("min_qty", 1), drop.get("max_qty", 1))
            weights = drop.get("rarity_weights", {})
            names, w = zip(*weights.items()) if weights else (["common"], [1.0])
            for _ in range(qty):
                rar = Rarity[rng.choices(names, w, k=1)[0].upper()]
                items.append(create_item(
                    drop["item_id"],
                    level=lvl,
                    grade=grade,
                    rarity=rar,
                    rng=rng
                ))
    return items

def roll_gold(enemy: Any, rng: random.Random) -> int:
    if hasattr(enemy, "gold_min") and hasattr(enemy, "gold_max"):
        lo, hi = enemy.gold_min, enemy.gold_max
        return rng.randint(lo, hi) if hi > lo else lo
    if hasattr(enemy, "gold"):
        return rng.randint(1, enemy.gold) if enemy.gold > 0 else 0
    return 0
