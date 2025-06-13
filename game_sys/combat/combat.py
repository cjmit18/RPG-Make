# game_sys/combat/combat.py

"""
Combat capabilities: damage calculation and loot handling.
Refactored to include defender's defense stat in every hit, not only when defending.
"""

import random
from typing import Any, Dict, Optional, List
from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.combat.loader import DROP_TABLES
from game_sys.items.factory import create_item
from game_sys.core.hooks import hook_dispatcher

log = get_logger(__name__)


class CombatCapabilities:
    """
    Handles 1-on-1 combat resolution and looting:
      - calculate_damage(attacker, defender, damage_map, ...)
      - roll_loot(defeated)
      - transfer_loot(winner, defeated)
    """

    def __init__(
        self,
        character: Any,
        enemy: Any,
        rng: Optional[random.Random] = None
    ) -> None:
        self.character = character
        self.enemy = enemy
        self.rng = rng or random.Random()

    def calculate_damage(
        self,
        attacker: Any,
        defender: Any,
        damage_map: Dict[DamageType, float],
        stat_name: Optional[str] = "attack",
        multiplier: float = 1.0,
        crit_chance: float = 0.10,
        variance: float = 0.10,
    ) -> str:
        """
        Compute and apply damage for each damage type in damage_map.
        Now includes defender.defense stat as a flat reduction before
        resistance multipliers and defending flag. Floors damage to
        a minimum of 10% of raw roll to avoid zeroing out.
        """
        parts: List[str] = []
        crit = False

        for dt, base in damage_map.items():
            # Base roll including attacker's stat bonus
            roll = base
            if stat_name:
                roll += getattr(attacker, stat_name, 0) * multiplier

            # Apply variance
            if variance > 0:
                roll *= self.rng.uniform(1 - variance, 1 + variance)

            # Critical hit check
            if self.rng.random() < crit_chance:
                roll *= 2
                crit = True

            raw_damage = int(round(roll))

            # Incorporate defender's defense stat (flat reduction)
            def_stat = getattr(defender, 'defense', 0)
            # Ensure minimum hit (10% floor)
            floor = max(int(round(raw_damage * 0.1)), 1)
            adjusted_raw = max(raw_damage - def_stat, floor)

            # Resistance × Weakness multiplier
            mult = (
                defender._resistance_multiplier(dt)
                if hasattr(defender, '_resistance_multiplier')
                else 1.0
            )
            dmg = int(round(adjusted_raw * mult))

            # Defending halves damage
            if getattr(defender, 'defending', False):
                dmg //= 2
                defender.defending = False

            # Pre-damage hook
            hook_dispatcher.fire(
                "combat.before_damage",
                attacker=attacker,
                defender=defender,
                amount=dmg,
                damage_type=dt
            )

            # Apply damage
            defender.take_damage(dmg, damage_type=dt)

            # Post-damage hook
            hook_dispatcher.fire(
                "combat.after_damage",
                attacker=attacker,
                defender=defender,
                amount=dmg,
                damage_type=dt
            )

            parts.append(f"{dmg} {dt.name.lower()}")

        # Build summary
        summary = f"{attacker.name} deals {' + '.join(parts)} to {defender.name}"
        if crit:
            summary += " (CRITICAL!)"
        if mult:
            summary += f" (after resistance/weakness ×{mult:.2f})"
        if defender.current_health == 0:
            summary += " and defeats them!"

        log.info(summary)
        return summary

    def roll_loot(self, defeated: Any) -> List[Any]:
        """
        Roll loot based on the defeated actor's type and level.
        Returns a list of items that were dropped.
        """
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

        # Find matching tier
        chosen = next(
            (
                tier for tier in tiers
                if (tier["min_level"] <= lvl <= tier["max_level"]
                    and tier.get("min_grade", 0) <= grade <= tier.get("max_grade", grade))
            ),
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
                from game_sys.core.rarity import Rarity
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
        """
        Transfer loot from defeated actor to the winner,
        including item drops and gold.
        """
        # Items
        looted: List[Any] = []
        for itm in self.roll_loot(defeated):
            winner.inventory.add_item(itm)
            looted.append(itm)
            log.info("%s looted 1x %s from %s.",
                     winner.name, itm.name, defeated.name)
        hook_dispatcher.fire("combat.loot_given", winner=winner, items=looted)

        # Gold
        gold_amt = 0
        if hasattr(defeated, "gold_min") and hasattr(defeated, "gold_max"):
            gm, gx = defeated.gold_min, defeated.gold_max
            gold_amt = self.rng.randint(gm, gx) if gx > gm else gm
        elif hasattr(defeated, "gold"):
            gold_amt = self.rng.randint(1, defeated.gold) if defeated.gold > 0 else 0

        if gold_amt > 0:
            winner.gold += gold_amt
            defeated.gold = 0
            log.info("%s looted %d gold from %s.",
                     winner.name, gold_amt, defeated.name)
        else:
            log.info("%s had no gold to drop.", defeated.name)
