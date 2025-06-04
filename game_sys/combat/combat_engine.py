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
    Runs a turn‐based fight loop until one side is wiped out or max_turns reached.
    """

    def __init__(
        self,
        party: Union[Actor, List[Actor]],
        enemies: Union[Actor, List[Actor]],
        *,
        rng: Optional[random.Random] = None,
        action_fn: Optional[Callable[[Actor], str]] = None,
        max_turns: int = 100,
    ):
        self.party: List[Actor] = party if isinstance(party, list) else [party]
        self.enemies: List[Actor] = enemies if isinstance(enemies, list) else [enemies]
        self.participants: List[Actor] = self.party + self.enemies
        self.rng = rng or random.Random()
        self.action_fn = action_fn or (lambda actor: "attack")
        self.max_turns = max_turns
        self.last_defeated: Optional[Actor] = None

        for actor in self.participants:
            actor.defending = False
            actor.last_damager = None

    def _turn_order(self) -> List[Actor]:
        return sorted(
            (actor for actor in self.participants if actor.health > 0),
            key=lambda actor: actor.speed,
            reverse=True,
        )

    def run(self) -> str:
        turn_count = 0
        log.info(
            "Combat started: Party [%s] vs. Enemies [%s]",
            ", ".join(p.name for p in self.party),
            ", ".join(e.name for e in self.enemies),
        )

        for actor in self.participants:
            actor.restore_all()
            actor.tick_statuses()

        while self.party and self.enemies:
            turn_count += 1
            if turn_count > self.max_turns:
                log.warning("Combat timed out after %d turns.", self.max_turns)
                return "Combat timed out."

            log.info("Turn %d begins.", turn_count)

            for actor in self._turn_order():
                if actor.health <= 0:
                    continue

                foes = self.enemies if actor in self.party else self.party
                if not foes:
                    break

                outcome = self._perform_actor_turn(actor, foes)
                if outcome:
                    log.info(outcome)

                if self.last_defeated:
                    self._handle_death(self.last_defeated)
                    self.last_defeated = None

                if not self.party or not self.enemies:
                    break

            for actor in list(self.participants):
                actor.tick_statuses()

            if not self.enemies:
                winners = ", ".join(p.name for p in self.party if p.health > 0)
                return f"{winners} win!"
            if not self.party:
                rem = ", ".join(e.name for e in self.enemies if e.health > 0)
                return f"Enemies ({rem}) win!"

        return "Draw?"

    def _perform_actor_turn(self, actor: Actor, foes: List[Actor]) -> Optional[str]:
        living_foes = [f for f in foes if f.health > 0]
        if not living_foes:
            return None

        target = self.rng.choice(living_foes)
        action = self.action_fn(actor).lower()

        combat = CombatCapabilities(actor, target, rng=self.rng)
        if action == "attack":
            result = combat.calculate_damage(actor, target, damage_type = DamageType.PHYSICAL)
            if target.health <= 0:
                target.last_damager = actor
                self.last_defeated = target
            return result

        elif action == "defend":
            actor.defending = True
            return f"{actor.name} defends."

        else:
            return f"{actor.name} does nothing."

    def _handle_death(self, target: Actor) -> None:
        killer = target.last_damager or target

        if target in self.enemies:
            CombatCapabilities(killer, target, rng=self.rng).loot(killer, target)
            if isinstance(target, Enemy):
                self._award_xp(target)
            self.enemies.remove(target)

        if target in self.party:
            self.party.remove(target)

        if target in self.participants:
            self.participants.remove(target)
        log.info("%s removed from combat.", target.name)

    def _award_xp(self, defeated: Enemy) -> None:
        xp = defeated.levels.experience
        if xp <= 0:
            return

        living_members = [member for member in self.party if member.health > 0]
        if not living_members:
            return

        share = xp // len(living_members)
        for member in living_members:
            member.levels.add_experience(share)
            log.info("%s receives %d XP from defeating %s.", member.name, share, defeated.name)
