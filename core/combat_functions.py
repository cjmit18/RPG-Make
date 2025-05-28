# core/combat_functions.py

"""This module contains the CombatCapabilities class for handling combat logic in a game."""
import logging
import random
from typing import Callable, List, Tuple, Optional, TYPE_CHECKING

# Only imported for static type checking to avoid runtime circular imports
if TYPE_CHECKING:
    from core.actor import Actor

log = logging.getLogger(__name__)

class CombatCapabilities:
    """Combat handler with injectable RNG and action provider."""

    def __init__(
        self,
        character: 'Actor',
        enemy: Optional['Actor'] = None,
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable[['Actor'], str]] = None,
    ) -> None:
        """
        Args:
            character: the active Actor
            enemy:     the opponent Actor (required for full loop)
            rng:       a random.Random instance for deterministic rolls
            action_fn: function taking an Actor and returning "attack"/"defend"
        """
        self.character = character
        self.enemy = enemy
        self.rng = rng or random.Random()
        self.action_fn = action_fn or self._default_action
        self.turn_count = 0

        # Initialize defending flags
        character.defending = False
        if enemy:
            enemy.defending = False

    def _default_action(self, actor: 'Actor') -> str:
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
                if defender.health <= 0:
                    return f"{attacker.name} wins!"
                self.turn_count += 1

    def _turn_order(self) -> List[Tuple['Actor', 'Actor']]:
        """
        Determines who goes first based on speed.
        Pure comparison, no I/O.
        """
        if self.character.speed >= self.enemy.speed:
            return [(self.character, self.enemy), (self.enemy, self.character)]
        return [(self.enemy, self.character), (self.character, self.enemy)]

    def _execute(
        self,
        attacker: 'Actor',
        defender: 'Actor',
        action: str
    ) -> str:
        """
        Core dispatch: no I/O, just logic.
        Returns the outcome string for this action.
        """
        if action == "attack":
            return self._attack(attacker, defender)
        if action == "defend":
            attacker.defending = True
            log.info(f"{attacker.name} defends.")
            return f"{attacker.name} defends."
        log.info(f"Unknown action '{action}' by {attacker.name}")
        return f"{attacker.name} does nothing."

    def _attack(
        self,
        attacker: 'Actor',
        defender: 'Actor'
    ) -> str:
        """
        Pure damage calculation & application.
        No direct prints: just state changes + return text.
        """
        # 1) compute base damage
        base = max(0.0, attacker.attack - defender.defense * 0.05)
        # 2) random multiplier
        mult = self.rng.uniform(0.8, 1.2)
        dmg_f = base * mult

        # 3) crit?
        is_crit = self.rng.random() < 0.1
        if is_crit:
            dmg_f *= 2

        # 4) defend?
        if defender.defending:
            dmg_f *= 0.5
            defender.defending = False

        # 5) finalize & apply (round to nearest int)
        dmg = round(dmg_f)
        defender.health -= dmg  # uses Actor.health setter (clamped)

        # 6) outcome string
        crit_text = " Critical Hit!" if is_crit else ""
        txt = f"{attacker.name} deals {dmg} damage.{crit_text}"
        log.info(txt)
        return txt

    def calculate_damage(
        self,
        attacker: 'Actor',
        defender: 'Actor'
    ) -> str:
        """
        One-off damage call (no turn logic).
        """
        return self._attack(attacker, defender)

    def check_defeat(self, character: 'Actor') -> bool:
        """Pure check—no I/O."""
        return character.health <= 0

    def loot(self, winner: 'Actor', loser: 'Actor') -> None:
        """
        Loot transfer with injectable RNG.
        No prints; uses log.info for auditing.
        """
        for slot in list(loser.inventory.items.values()):
            item = slot["item"]
            qty_available = slot["quantity"]
            qty = self.rng.randint(1, qty_available)
            winner.inventory.add_item(item, qty)
            log.info(f"{winner.name} loots {qty}×{item.name} from {loser.name}.")
        loser.inventory.drop_all()

# Alias for backward compatibility (tests or legacy code expecting `Combat`)
Combat = CombatCapabilities
