# game_sys/combat/combat_engine.py

import random
from typing import List, Optional, Callable, Union

from logs.logs import get_logger
from game_sys.core.damage_types import DamageType
from game_sys.core.actor import Actor
from game_sys.combat.combat import CombatCapabilities
from game_sys.character.character_creation import Enemy

log = get_logger(__name__)


class CombatEngine:
    """
    Runs a turn-based fight loop until one side is wiped out or max_turns reached.
    """

    def __init__(
        self,
        party: Union[Actor, List[Actor]],
        enemies: Union[Actor, List[Actor]],
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable[[Actor], str]] = None,
        max_turns: int = 100,
    ):
        # Wrap single Actor into a list if necessary
        if isinstance(party, Actor):
            self.party: List[Actor] = [party]
        else:
            self.party = list(party)

        if isinstance(enemies, Actor):
            self.enemies: List[Actor] = [enemies]
        else:
            self.enemies = list(enemies)

        self.rng = rng or random.Random()

        # If no action_fn provided, default to "attack" every time
        self.action_fn = action_fn or (lambda actor: "attack")

        self.max_turns = max_turns

    def run(self) -> str:
        """
        Loop through turns until one side is wiped out or max_turns is reached.
        Returns a summary string of who won (or “Draw?”).
        """
        for turn in range(1, self.max_turns + 1):
            # 1) Party members act in order
            for member in self.party:
                if member.current_health <= 0:
                    continue  # dead actors can’t act
                result = self._perform_actor_turn(member, self.enemies)
                if result:
                    return result

            # 2) Enemies act in order
            for foe in self.enemies:
                if foe.current_health <= 0:
                    continue
                result = self._perform_actor_turn(foe, self.party)
                if result:
                    return result

        # If we exit the loop without either side dying...
        return "Draw?"

    def _perform_actor_turn(self, actor: Actor, foes: List[Actor]) -> Optional[str]:
        """
        Let ‘actor’ take an action against one randomly chosen foe (among those still alive).
        If the action kills the target, award XP and loot. Return a “win/lose” string if
        the fight is over, otherwise return None.
        """
        # 1) Filter out only living foes
        living_foes = [f for f in foes if f.current_health > 0]
        if not living_foes:
            # If no foes remain alive, actor’s side has won
            if actor in self.party:
                survivors = [e.name for e in self.enemies if e.current_health > 0]
                return f"Party wins! (Enemies still alive: {', '.join(survivors)})"
            else:
                survivors = [m.name for m in self.party if m.current_health > 0]
                return f"Enemies win! (Party still alive: {', '.join(survivors)})"

        # 2) Choose a random living foe
        target = self.rng.choice(living_foes)
        action = self.action_fn(actor).lower()

        # 3) Build a CombatCapabilities instance for attacker/defender
        combat = CombatCapabilities(actor, target, rng=self.rng)

        # 4) Dispatch on action
        if action == "attack":
            # (a) Compute base physical damage: actor.attack – (target.defense × 0.05)
            base_amount = actor.attack - (target.defense * 0.05)
            base_amount = max(0, base_amount)

            # (b) Roll for small variance (±10%) and a 10% crit chance
            variance_factor = 1.0 + self.rng.uniform(-0.1, 0.1)
            is_crit = self.rng.random() < 0.10  # 10% chance
            if is_crit:
                variance_factor += 0.25  # +25% for critical

            # (c) Final damage after variance & crit
            adjusted_amount = max(0, int(round(base_amount * variance_factor)))

            # (d) Build damage_map and call calculate_damage
            dmg_map = {DamageType.PHYSICAL: adjusted_amount}
            combat.calculate_damage(
                attacker=actor,
                defender=target,
                damage_map=dmg_map
            )

        elif action == "defend":
            actor.defending = True
            log.info("%s is defending this turn.", actor.name)

        else:
            # Unknown action: fallback to a plain physical attack without variance/crit
            base_amount = actor.attack - (target.defense * 0.05)
            base_amount = max(0, base_amount)
            dmg_map = {DamageType.PHYSICAL: int(round(base_amount))}
            combat.calculate_damage(
                attacker=actor,
                defender=target,
                damage_map=dmg_map
            )

        # 5) After applying damage, check if target died
        if target.current_health <= 0:
            # (a) Award XP
            if isinstance(target, Enemy):
                self._award_xp(target)

            # (b) Transfer loot (gold + items)
            combat.transfer_loot(actor, target)

            # (c) Check if the target's side is wiped out
            if target in self.enemies:
                remaining_enemies = [e for e in self.enemies if e.current_health > 0]
                if not remaining_enemies:
                    return "Party wins! (All enemies defeated)"
            else:
                remaining_party = [m for m in self.party if m.current_health > 0]
                if not remaining_party:
                    return "Enemies win! (All party members defeated)"

        return None

    def _award_xp(self, defeated: Enemy) -> None:
        """
        Split the defeated enemy’s experience among all living party members.
        """
        xp = defeated.levels.experience
        if xp <= 0:
            return

        living_members = [m for m in self.party if m.current_health > 0]
        if not living_members:
            return

        share = xp // len(living_members)
        for member in living_members:
            member.levels.add_experience(share)
            log.info("%s receives %d XP from defeating %s.", member.name, share, defeated.name)
