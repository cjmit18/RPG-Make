"""
This module contains the CombatCapabilities class 
for handling combat and loot logic in a game.
"""

import json
import random
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Tuple,
    Union,
)

from logs.logs import get_logger
from game_sys.items.factory import create_item
from game_sys.items.item_base import Item

log = get_logger(__name__)

if TYPE_CHECKING:
    from game_sys.core.actor import Actor
    from game_sys.character.character_creation import Enemy

# -------------------------------------------------------------------------------
# Constants for combat
# -------------------------------------------------------------------------------
CRIT_CHANCE: float = 0.10
DAMAGE_VARIANCE_MIN: float = 0.8
DAMAGE_VARIANCE_MAX: float = 1.2
DEFENSE_SCALING: float = 0.05

# -------------------------------------------------------------------------------
# 1) LOAD DROP TABLES FROM JSON
# -------------------------------------------------------------------------------
_DROP_TABLES_PATH = Path(__file__).parent / "data" / "drop_tables.json"
try:
    with open(_DROP_TABLES_PATH, "r", encoding="utf-8") as f:
        _RAW_DROP_TABLES: dict[str, List[dict]] = json.load(f)
except FileNotFoundError:
    _RAW_DROP_TABLES = {}

# DROP_TABLES maps job_id -> list of (factory, chance, min_qty, max_qty)
DROP_TABLES: dict[str, List[Tuple[Callable[[], Item], float, int, int]]] = {}

for job_id, entries in _RAW_DROP_TABLES.items():
    parsed_list: List[Tuple[Callable[[], Item], float, int, int]] = []
    for entry in entries:
        template_id = entry["template_id"]
        chance = float(entry["chance"])
        min_q = int(entry["min_qty"])
        max_q = int(entry["max_qty"])
        # Each factory returns a fresh Item instance
        factory = lambda tid=template_id: create_item(tid)
        parsed_list.append((factory, chance, min_q, max_q))
    DROP_TABLES[job_id] = parsed_list


# -------------------------------------------------------------------------------
# 2) CombatCapabilities Class
# -------------------------------------------------------------------------------
class CombatCapabilities:
    """
    Combat handler with injectable RNG, action provider, and separated loot logic.
    """

    def __init__(
        self,
        character: "Actor",
        enemy: Optional["Actor"] = None,
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable[["Actor"], str]] = None,
        on_turn: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Args:
            character: the active Actor (e.g., player)
            enemy:     the opponent Actor (for single‐combat loops)
            rng:       a random.Random instance for deterministic rolls
            action_fn: function taking an Actor -> "attack"/"defend"
            on_turn:   callback invoked each turn with the outcome string
        """
        self.character = character
        self.enemy = enemy
        self.rng = rng if rng is not None else random.Random()
        self.action_fn = action_fn if action_fn is not None else self._default_action
        self.on_turn = on_turn if on_turn is not None else (lambda outcome: None)
        self.turn_count = 0

        # Initialize defending flags
        character.defending = False
        if enemy:
            enemy.defending = False

    def _default_action(self, actor: "Actor") -> str:
        """Console‐based fallback I/O (outside core logic)."""
        return input(f"{actor.name}, action? (attack/defend): ").strip().lower()

    def start_combat_loop(self) -> str:
        """
        Executes turns until one side is defeated.
        Returns a summary string like "Hero wins!".
        """
        if not self.enemy:
            raise ValueError("Enemy must be provided for full combat loop")

        while True:
            for attacker, defender in self._turn_order():
                action = self.action_fn(attacker)
                outcome = self._execute(attacker, defender, action)
                self.on_turn(outcome)

                if defender.health <= 0:
                    return f"{attacker.name} wins!"
                self.turn_count += 1

    def _turn_order(self) -> List[Tuple["Actor", "Actor"]]:
        """
        Determines who goes first based on speed.
        Pure comparison, no I/O.
        """
        if self.character.speed >= self.enemy.speed:
            return [(self.character, self.enemy), (self.enemy, self.character)]
        return [(self.enemy, self.character), (self.character, self.enemy)]

    def _execute(
        self,
        attacker: "Actor",
        defender: "Actor",
        action: str,
    ) -> str:
        """
        Core dispatch: no I/O, just logic.
        Returns the outcome string for this action.
        """
        action_lower = action.lower()
        if action_lower == "attack":
            return self._attack(attacker, defender)
        if action_lower == "defend":
            attacker.defending = True
            log.info(f"{attacker.name} defends.")
            return f"{attacker.name} defends."
        log.info(f"Unknown action '{action}' by {attacker.name}")
        return f"{attacker.name} does nothing."

    def _attack(
        self,
        attacker: "Actor",
        defender: "Actor",
    ) -> str:
    
        """
        Pure damage calculation & application.
        No direct prints: just state changes + return text.
        """
        # 1) Compute base damage
        base_damage = max(0.0, attacker.attack - defender.defense * DEFENSE_SCALING)

        # 2) Apply random variance
        variance = self.rng.uniform(DAMAGE_VARIANCE_MIN, DAMAGE_VARIANCE_MAX)
        dmg_float = base_damage * variance

        # 3) Check for critical hit
        is_crit = self.rng.random() < CRIT_CHANCE
        if is_crit:
            dmg_float *= 2.0

        # 4) If defender is defending, halve damage and reset flag
        if defender.defending:
            dmg_float *= 0.5
            defender.defending = False

        # 5) Finalize & apply damage (round to nearest int)
        dmg = round(dmg_float)
        defender.health -= dmg  # uses Actor.health setter (clamped at zero)

        # 6) Build outcome string
        crit_text = " Critical Hit!" if is_crit else ""
        return f"{attacker.name} deals {dmg} damage.{crit_text}"

    def calculate_damage(
        self,
        attacker: "Actor",
        defender: "Actor",
    ) -> str:
        """
        One-off damage call without involving turn loop.
        Returns same outcome string as _attack.
        """
        return self._attack(attacker, defender)

    def check_defeat(self, character: "Actor") -> bool:
        """Pure check—no I/O. Returns True if health <= 0."""
        return character.health <= 0

    # ----------------------------------------------------------------------------
    # 3) LOOT LOGIC: Separate roll_loot() and transfer_loot()
    # ----------------------------------------------------------------------------

    def roll_loot(self, defeated: "Actor") -> List[Tuple[Union[Item, str], int]]:
        """
        Roll the drop table for this foe's job (using job.name.lower()).
        If defeated is an Enemy, only drop from the JSON table.
        Otherwise, include carried items.

        Returns a list of (Item instance OR item_id string, quantity).
        Does NOT modify any inventories.
        """
        drops: List[Tuple[Union[Item, str], int]] = []
        job_id = defeated.job.name.lower()

        # 1) “New drops” via JSON‐driven DROP_TABLES
        for factory, chance, min_qty, max_qty in DROP_TABLES.get(job_id, []):
            if self.rng.random() <= chance:
                quantity = min_qty if min_qty == max_qty else self.rng.randint(min_qty, max_qty)
                new_item = factory()
                drops.append((new_item, quantity))
                log.info(f"Rolled drop from {job_id}: {new_item.name} ×{quantity}")

        # 2) If defeated is NOT an Enemy, include carried items (by ID)
        from game_sys.character.character_creation import Enemy as _EnemyType

        if not isinstance(defeated, _EnemyType):
            for slot in defeated.inventory.items.values():
                item_id: str = slot["item"]       # inventory stores IDs as strings
                qty_available: int = slot["quantity"]
                if qty_available > 0:
                    drops.append((item_id, qty_available))
                    log.info(
                        f"{defeated.name} carried {item_id} ×{qty_available} → potential loot: {qty_available}"
                    )

        return drops

    def transfer_loot(self, winner: "Actor", defeated: "Actor") -> None:
        """
        Remove carried items from defeated.inventory and add to winner.inventory,
        then add all “new drops” as fresh stacks.
        """
        loot_list = self.roll_loot(defeated)
        if not loot_list:
            log.info(f"No loot for {winner.name} from defeating {defeated.name}.")
            return

        for item_obj, qty in loot_list:
            # CASE A: carried‐item (item_obj is a string ID)
            if isinstance(item_obj, str):
                # 1) Remove by ID from defeated’s inventory
                defeated.inventory.remove_item(item_obj, qty)
                # 2) Create a fresh Item for the winner
                real_item = create_item(item_obj)
                winner.inventory.add_item(real_item, qty)
                log.info(f"{winner.name} loots {qty}×{real_item.name} from {defeated.name}")

            # CASE B: “New drop” (item_obj is already an Item instance)
            else:
                winner.inventory.add_item(item_obj, qty)
                log.info(f"{winner.name} receives {qty}×{item_obj.name} as a drop.")

        # Optionally prune zero‐quantity slots from defeated
        if hasattr(defeated.inventory, "compact"):
            defeated.inventory.compact()
        elif hasattr(defeated.inventory, "remove_empty_slots"):
            defeated.inventory.remove_empty_slots()

    def loot(self, winner: "Actor", loser: "Actor") -> None:
        """
        Backward‐compatible alias for transfer_loot().
        """
        self.transfer_loot(winner, loser)


# Alias for backward compatibility
Combat = CombatCapabilities
