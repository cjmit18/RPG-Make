"""This module contains the Combat class for handling combat logic in a game."""
from __future__ import annotations
import enum
import logging
import random
from typing import Callable, List, Tuple

import core.character_creation as character_creation
from core.character_creation import Character, Player

log = logging.getLogger(__name__)

class Combat:
    """Combat handler with injectable RNG and action provider."""

    def __init__(
        self,
        character: Character,
        enemy: Character,
        rng: random.Random | None = None,
        action_fn: Callable[[Character], str] | None = None,
    ) -> None:
        """
        Args:
            character: the player Character
            enemy:     the opponent Character
            rng:       a random.Random instance for deterministic rolls
            action_fn: function taking a Character and returning "attack"/"defend"
        """
        self.character   = character
        self.enemy       = enemy
        self.rng         = rng or random.Random()
        # If no action_fn is provided, fall back to console input (outside core logic)
        self.action_fn   = action_fn or self._default_action
        self.turn_count  = 0

        # Initialize typed 'defending' flag on both fighters
        character.defending = False
        enemy.defending     = False

    def _default_action(self, actor: Character) -> str:
        """Console‐based fallback I/O (outside core logic)."""
        return input(f"{actor.name}, action? (attack/defend): ").strip().lower()

    def start_combat_loop(self) -> str:
        """
        Executes turns until one side is defeated.
        Returns a summary string like "Hero wins!".
        """
        while True:
            for attacker, defender in self._turn_order():
                action  = self.action_fn(attacker)
                outcome = self._execute(attacker, defender, action)
                if defender.health <= 0:
                    return f"{attacker.name} wins!"
                self.turn_count += 1

    def _turn_order(self) -> List[Tuple[Character, Character]]:
        """
        Determines who goes first based on speed.
        No I/O here—just pure comparison.
        """
        if self.character.speed >= self.enemy.speed:
            return [(self.character, self.enemy), (self.enemy, self.character)]
        return [(self.enemy, self.character), (self.character, self.enemy)]

    def _execute(
        self,
        attacker: Character,
        defender: Character,
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
        attacker: Character,
        defender: Character
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

        # 5) finalize & apply
        dmg = int(dmg_f)
        defender.health -= dmg  # uses Character.health setter (clamped)

        # 6) assemble outcome string
        crit_text = " Critical Hit!" if is_crit else ""
        txt = f"{attacker.name} deals {dmg} damage.{crit_text}"
        log.info(txt)
        return txt

    def calculate_damage(
        self,
        attacker: Character,
        defender: Character
    ) -> str:
        """
        Legacy-friendly entrypoint for damage only.
        Delegates to the new _attack() logic.
        """
        return self._attack(attacker, defender)

    def check_defeat(self, character: Character) -> bool:
        """Pure check—no I/O."""
        return character.health <= 0

    def loot(self, winner: Character, loser: Character) -> None:
        """
        Loot transfer with injectable RNG.
        No prints; uses log.info for auditing.
        """
        for slot in list(loser.inventory.items.values()):
            item          = slot["item"]
            qty_available = slot["quantity"]
            qty           = self.rng.randint(1, qty_available)
            winner.inventory.add_item(item, qty)
            log.info(f"{winner.name} loots {qty}×{item.name} from {loser.name}.")
        loser.inventory.drop_all()
