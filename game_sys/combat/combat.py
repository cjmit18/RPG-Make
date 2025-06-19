# game_sys/combat/combat.py

"""
Combat capabilities: damage calculation and loot handling.
Refactored to include:
- total_damage_map for enchantment + item synergy,
- resistance multipliers (actor & gear),
- CRITs and variance scaling,
- post-resist hook flow.
"""

import random
from typing import Any, Dict, Optional, List
from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.combat.loader import DROP_TABLES
from game_sys.items.factory import create_item
from game_sys.core.hooks import hook_dispatcher
from game_sys.core.rarity import Rarity
from game_sys.items.item_base import EquipableItem

log = get_logger(__name__)

class CombatCapabilities:
    def __init__(self, character: Any, enemy: Any, rng: Optional[random.Random] = None) -> None:
        self.character = character
        self.enemy = enemy
        self.rng = rng or random.Random()

    def calculate_damage(
        self,
        attacker: Any,
        defender: Any,
        damage_map: Optional[Dict[DamageType, float]],
        stat_name: Optional[str],
        multiplier: float = 1.0, # Multiplier for stat scaling
        crit_chance: float = 0.10, # 10% chance of critical hit
        variance: float = 0.10, # 10% variance in damage output
    ) -> str:
        parts: List[str] = []
        crit = False
        resist_mult: float = 1.0
        # Correctly resolve equipped weapon object
        if damage_map and hasattr(attacker, "inventory"):
            weapon = attacker.inventory.get_primary_weapon()
        if isinstance(weapon, EquipableItem):
            damage_map = weapon.total_damage_map()
        # Defensive fallback if map is missing or zeroed
        if not damage_map or sum(damage_map.values()) <= 0:
            log.warning("No elemental damage found; falling back to physical for %s", attacker.name)
            fallback_stat = getattr(attacker, stat_name, 1) if stat_name else 1
            damage_map = {DamageType.FIRE: fallback_stat}
        for dt, base in damage_map.items():
            roll = base
            if stat_name:
                roll += getattr(attacker, stat_name, 0) * multiplier

            if variance > 0:
                roll *= self.rng.uniform(1 - variance, 1 + variance)

            if self.rng.random() < crit_chance:
                roll *= 2
                crit = True

            raw = int(round(roll))
            def_stat = getattr(defender, 'defense', 0)
            floor = max(int(round(raw * 0.1)), 1)
            reduced = max(raw - def_stat, floor)

            resist_mult = 1.0
            if hasattr(defender, '_resistance_multiplier'):
                resist_mult = defender._resistance_multiplier(dt)

            dmg = int(round(reduced * resist_mult))

            if getattr(defender, 'defending', False):
                dmg //= 2
                defender.defending = False

            log.info("%s hits %s for %d %s damage.", attacker.name, defender.name, dmg, dt.name.lower())

            hook_dispatcher.fire("combat.before_damage", attacker=attacker, defender=defender, amount=dmg, damage_type=dt)
            defender.take_damage(dmg, damage_type=dt)
            hook_dispatcher.fire("combat.after_damage", attacker=attacker, defender=defender, amount=dmg, damage_type=dt)

            parts.append(f"{dmg} {dt.name.lower()}")

        summary = f"{attacker.name} deals {' + '.join(parts)} to {defender.name}"
        if crit:
            summary += " (CRITICAL!)"
        if resist_mult != 1.0:
            summary += f" (after resistance ×{resist_mult:.2f})"
        if getattr(defender, 'current_health', 1) <= 0:
            summary += " and defeats them!"

        log.info(summary)
        return summary

    def roll_loot(self, defeated: Any) -> List[Any]:
        hook_dispatcher.fire("combat.loot_roll", enemy=defeated)
        items: List[Any] = []
        key = (
            defeated.job.job_id.lower()
            if hasattr(defeated, "job") and defeated.job
            else type(defeated).__name__.lower()
        )
        tiers = DROP_TABLES.get(key, [])
        lvl = getattr(defeated, "level", 1)
        grade = getattr(defeated, "grade", 1)

        chosen = next(
            (tier for tier in tiers if (tier["min_level"] <= lvl <= tier["max_level"] and tier.get("min_grade", 0) <= grade <= tier.get("max_grade", grade))),
            None
        )
        if not chosen:
            return items

        for drop in chosen["drops"]:
            if self.rng.random() <= drop.get("chance", 0):
                qty = self.rng.randint(drop.get("min_qty", 1), drop.get("max_qty", 1))
                rar_weights = drop.get("rarity_weights", {"common": 1.0})
                names, weights = zip(*rar_weights.items())
                rar_name = self.rng.choices(names, weights)[0]
                rarity_enum = Rarity[rar_name.upper()]

                for _ in range(qty):
                    item = create_item(
                        drop["item_id"],
                        level=lvl,
                        grade=grade,
                        rarity=rarity_enum,
                        rng=self.rng
                    )
                    items.append(item)

        return items

    def transfer_loot(self, winner: Any, defeated: Any) -> None:
        looted: List[Any] = []
        for itm in self.roll_loot(defeated):
            winner.inventory.add_item(itm)
            looted.append(itm)
            log.info("%s looted 1x %s from %s.", winner.name, itm.name, defeated.name)

        hook_dispatcher.fire("combat.loot_given", winner=winner, items=looted)

        gold_amt = 0
        if hasattr(defeated, "gold_min") and hasattr(defeated, "gold_max"):
            gm, gx = defeated.gold_min, defeated.gold_max
            gold_amt = self.rng.randint(gm, gx) if gx > gm else gm
        elif hasattr(defeated, "gold"):
            gold_amt = self.rng.randint(1, defeated.gold) if defeated.gold > 0 else 0

        if gold_amt > 0:
            winner.gold += gold_amt
            defeated.gold = 0
            log.info("%s looted %d gold from %s.", winner.name, gold_amt, defeated.name)
        else:
            log.info("%s had no gold to drop.", defeated.name)