# game_sys/combat/combat.py
import random
from typing import Dict, Optional
from logs.logs import get_logger
from game_sys.core.actor import Actor
from game_sys.core.damage_types import DamageType
from game_sys.combat.drop_tables import DROP_TABLES
from game_sys.items.factory import create_item

log = get_logger(__name__)


class CombatCapabilities:
    """
    Handles 1-on-1 combat resolution and looting.
      - calculate_damage(attacker, defender, damage_map, …)
      - roll_loot(defeated)
      - transfer_loot(winner, defeated)
    """

    def __init__(self, character: Actor, enemy: Actor, rng: Optional[random.Random] = None):
        self.character = character
        self.enemy = enemy
        self.rng = rng or random.Random()

    def calculate_damage(
        self,
        attacker: Actor,
        defender: Actor,
        damage_map: Dict[DamageType, float],
        stat_name: Optional[str] = None,
        multiplier: float = 1.0,
        crit_chance: float = 0.0,
        variance: float = 0.0,
    ) -> str:
        """
        Multi-type damage resolution. For each (dtype → base_amount) pair in damage_map:
          1) Combine base_amount + (attacker.stat * multiplier) if stat_name is given
          2) Apply random variance and potential crit
          3) Multiply by weakness/resistance
          4) Halve if defender.defending
          5) Call defender.take_damage(final)
        Returns a concatenated log string (one block per DamageType).
        """
        log_parts = []

        for dtype, base_amount in damage_map.items():
            # (A) Compute raw from base_amount + stat scaling
            raw = base_amount
            if stat_name:
                stat_val = getattr(attacker.stats, stat_name, 0)
                raw += stat_val * multiplier

            # (B) Apply variance
            var_roll = raw * self.rng.uniform(1 - variance, 1 + variance)

            # (C) Crit check
            is_crit = False
            if self.rng.random() < crit_chance:
                var_roll *= 2
                is_crit = True

            # (D) Weakness / Resistance multipliers
            weak = defender.get_weakness_multiplier(dtype)
            resist = defender.get_resistance_multiplier(dtype)
            adjusted = round(var_roll * weak * resist)

            # (E) If defender is defending, halve and reset defending flag
            if defender.defending:
                adjusted = round(adjusted * 0.5)
                defender.defending = False

            # (F) Actually deal the damage (clamped by Actor.take_damage)
            defender.take_damage(adjusted)

            # (G) Build per-type log line
            part = f"{attacker.name} deals {adjusted} {dtype.name} damage."
            if is_crit:
                part += " (CRITICAL HIT!)"
            if weak != 1.0:
                part += f"\n(Weakness multiplier: {weak}×)"
            if resist != 1.0:
                part += f"\n(Resistance multiplier: {resist}×)"
            log_parts.append(part)

        return "\n".join(log_parts)

    def roll_loot(self, defeated: Actor) -> list:
        """
        Roll and return a list of items dropped by the defeated actor.
        """
        items = []
        table = DROP_TABLES.get(type(defeated).__name__, {})
        for item_id, chance in table.items():
            if self.rng.random() < chance:
                items.append(create_item(item_id))
        return items

    def transfer_loot(self, winner: Actor, defeated: Actor) -> None:
        """
        Transfer both items and gold from defeated to winner.
        """
        # (1) Transfer items
        items = self.roll_loot(defeated)
        for item in items:
            winner.inventory.add_item(item)
            log.info("%s looted %s from %s.", winner.name, item.name, defeated.name)

        # (2) Transfer gold
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
            winner.gold = getattr(winner, "gold", 0) + gold_amt
            log.info("%s looted %d gold from %s.", winner.name, gold_amt, defeated.name)
        else:
            log.info("%s had no gold to drop.", defeated.name)
