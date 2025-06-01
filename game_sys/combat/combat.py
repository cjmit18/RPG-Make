# game_sys/combat/combat.py

import random
from typing import Optional
from logs.logs import get_logger
from game_sys.core.actor import Actor
from game_sys.combat.drop_tables import DROP_TABLES
from game_sys.items.factory import create_item
from game_sys.items.item_base import Equipable

log = get_logger(__name__)


class CombatCapabilities:
    """
    Handles 1-on-1 combat resolution and looting.
      - calculate_damage(attacker, defender)
      - roll_loot(defeated)
      - transfer_loot(winner, defeated)
    """

    def __init__(self, character: Actor, enemy: Actor, rng: Optional[random.Random] = None):
        self.character = character
        self.enemy = enemy
        self.rng = rng or random.Random()

    def calculate_damage(self, attacker: Actor, defender: Actor) -> str:
        """
        Compute and apply damage:
          - base = attack − (defense * 0.05)
          - variance = uniform(0,1)
          - crit if random() < 0.1 ⇒ ×2
          - round final; halve if defender.defending.
        """
        base = attacker.attack - (defender.defense * 0.05)
        variance = self.rng.uniform(0, 1)
        damage = base * variance

        is_crit = False
        if self.rng.random() < 0.1:
            damage *= 2
            is_crit = True

        final = round(damage)
        if defender.defending:
            final = round(final * 0.5)
            defender.defending = False

        defender.take_damage(final)
        result = f"{attacker.name} deals {final} damage"
        if is_crit:
            result += ". Critical Hit!"
        return result

    def roll_loot(self, defeated: Actor):
        """
        Look up DROP_TABLES[job_id], find the matching level‐bucket, and
        roll each drop entry: return list of (Item, quantity).
        """
        drops = []
        job_id = None
        if getattr(defeated, "job", None) and defeated.job.name:
            job_id = defeated.job.name.lower()

        if job_id not in DROP_TABLES:
            log.info("No drop table for job '%s'; skipping item drops from %s.",
                     job_id or "(none)", defeated.name)
            return drops

        enemy_level = defeated.levels.lvl
        buckets = DROP_TABLES[job_id]
        matching = None
        for bucket in buckets:
            if bucket["min_level"] <= enemy_level <= bucket["max_level"]:
                matching = bucket
                break

        if not matching:
            log.info(
                "No drop-bucket for '%s' at level %d; skipping items from %s.",
                job_id, enemy_level, defeated.name
            )
            return drops

        for entry in matching["drops"]:
            item_id = entry["item_id"]
            chance = float(entry["chance"])
            min_q = int(entry["min_qty"])
            max_q = int(entry["max_qty"])

            roll = self.rng.random()
            if roll <= chance:
                qty = self.rng.randint(min_q, max_q)
                try:
                    item_obj = create_item(item_id)
                    drops.append((item_obj, qty))
                    log.info(
                        "%s looted %d× %s from %s (level %d). [%.2f ≤ %.2f]",
                        self.character.name, qty, item_obj.name, defeated.name,
                        enemy_level, roll, chance
                    )
                except Exception:
                    log.warning(
                        "Failed to create looted item '%s' for %s.",
                        item_id, self.character.name
                    )
            else:
                log.debug(
                    "%s rolled %.2f > %.2f: no '%s' from %s.",
                    self.character.name, roll, chance, item_id, defeated.name
                )
        return drops

    def transfer_loot(self, winner: Actor, defeated: Actor) -> None:
        """
        Mint dropped items (via roll_loot) into the winner's inventory.
        """
        drops = self.roll_loot(defeated)
        for item_obj, qty in drops:
            # always quantity=qty, never auto-equip
            winner.inventory.add_item(item_obj, quantity=qty, auto_equip=False)

    def loot(self, killer: Actor, defeated: Actor) -> None:
        """
        Legacy alias: transfer_loot(killer, defeated) + gold logic.
        """
        # 1) Items
        self.transfer_loot(killer, defeated)

        # 2) Gold
        gold_amt = 0
        if hasattr(defeated, "gold_min") and hasattr(defeated, "gold_max"):
            gm = getattr(defeated, "gold_min", 0)
            gx = getattr(defeated, "gold_max", gm)
            gold_amt = self.rng.randint(gm, gx) if gx > gm else gm
        elif hasattr(defeated, "gold"):
            avail = getattr(defeated, "gold", 0)
            if avail > 0:
                gold_amt = self.rng.randint(1, avail)

        if gold_amt:
            killer.gold = getattr(killer, "gold", 0) + gold_amt
            log.info("%s looted %d gold from %s.", killer.name, gold_amt, defeated.name)
        else:
            log.info("%s had no gold to drop.", defeated.name)
