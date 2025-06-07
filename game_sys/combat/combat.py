# File: game_sys/combat/combat.py

import random
from typing import Dict, Optional

from logs.logs import get_logger
from game_sys.character.actor import Actor
from game_sys.core.damage_types import DamageType
from game_sys.combat.drop_tables import DROP_TABLES
from game_sys.items.factory import create_item

log = get_logger(__name__)


class CombatCapabilities:
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
        
        for dtype, base_amount in damage_map.items():
            raw = base_amount
            if stat_name:
                raw += getattr(attacker.stats, stat_name, 0) * multiplier

            var_roll = raw * self.rng.uniform(1 - variance, 1 + variance)
            is_crit = self.rng.random() < crit_chance
            if is_crit:
                var_roll *= 2

            weak = defender.get_weakness_multiplier(dtype)
            resist = defender.get_resistance_multiplier(dtype)
            adjusted = round(var_roll * weak * resist)

            if defender.defending:
                adjusted = round(adjusted * 0.5)
                defender.defending = False

            defender.take_damage(adjusted, damage_type=dtype)

    def roll_loot(self, defeated: Actor) -> list:
        items = []
        table = DROP_TABLES.get(type(defeated).__name__, {})
        for item_id, chance in table.items():
            if self.rng.random() < chance:
                items.append(create_item(item_id))
        return items

    def transfer_loot(self, winner: Actor, defeated: Actor) -> None:
        for itm in self.roll_loot(defeated):
            winner.inventory.add_item(itm)
            log.info("%s looted 1× %s from %s.", winner.name, itm.name, defeated.name)

        gold_amt = 0
        if hasattr(defeated, "gold_min") and hasattr(defeated, "gold_max"):
            gm, gx = defeated.gold_min, defeated.gold_max
            gold_amt = self.rng.randint(gm, gx) if gx > gm else gm
        elif hasattr(defeated, "gold"):
            gold_amt = self.rng.randint(1, defeated.gold) if defeated.gold > 0 else 0

        if gold_amt:
            winner.gold += gold_amt
            log.info("%s looted %d gold from %s.", winner.name, gold_amt, defeated.name)
        else:
            log.info("%s had no gold to drop.", defeated.name)
