# game_sys/skills/skills.py

from __future__ import annotations
from typing import Any, Dict, List, Union

import logging

log = logging.getLogger(__name__)


class Skill:
    """
    A minimal Skill instance created from SkillRecord.
    Tracks id, name, mana_cost, stamina_cost, cooldown, and effects.
    """

    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        mana_cost: int,
        stamina_cost: int,
        cooldown: int,
        effects: List[Any],
    ) -> None:
        self.id: str = skill_id
        self.name: str = name
        self.description: str = description
        self.mana_cost: int = mana_cost
        self.stamina_cost: int = stamina_cost
        self.cooldown: int = cooldown
        self.effects: List[Any] = list(effects)
        self._current_cooldown: int = 0

    def can_cast(self, actor: Any) -> bool:
        """
        Return True if actor has enough mana/stamina and cooldown is zero.
        """
        if not isinstance(self.mana_cost, int) or not isinstance(self.stamina_cost, int):
            log.error("Skill '%s' has non-integer cost values.", self.id)
            return False

        has_resources = (
            actor.current_mana >= self.mana_cost and
            actor.current_stamina >= self.stamina_cost
        )
        is_off_cooldown = self._current_cooldown == 0
        return has_resources and is_off_cooldown

    def cast(self, actor: Any, target: Any) -> None:
        """
        Apply each effect to the target, deduct resources from actor, then set cooldown.
        Assumes each Effect has an apply(caster, target) method.
        """
        if not self.can_cast(actor):
            log.warning(
                "Actor '%s' cannot cast skill '%s': insufficient resources or on cooldown.",
                actor.name,
                self.id,
            )
            return

        # Deduct resources
        actor.mana = actor.current_mana - self.mana_cost
        actor.stamina = actor.current_stamina - self.stamina_cost

        log.info(
            "%s casts '%s' on %s (ManaCost=%d, StaminaCost=%d).",
            actor.name,
            self.name,
            getattr(target, "name", target),
            self.mana_cost,
            self.stamina_cost,
        )

        # Apply each effect in sequence
        for eff in self.effects:
            try:
                eff.apply(actor, target)
                log.debug(
                    "Effect '%s' applied by skill '%s'.",
                    type(eff).__name__,
                    self.id,
                )
            except Exception as e:
                log.exception(
                    "Error applying effect '%s' of skill '%s': %s",
                    type(eff).__name__,
                    self.id,
                    e,
                )

        # Set cooldown
        self._current_cooldown = self.cooldown
        log.debug("Skill '%s' cooldown set to %d.", self.id, self.cooldown)

    def tick_cooldown(self) -> None:
        """
        Decrement cooldown by 1 (clamped at zero).
        """
        if self._current_cooldown > 0:
            self._current_cooldown -= 1
            log.debug(
                "Skill '%s' cooldown decremented; now %d.",
                self.id,
                self._current_cooldown,
            )
