# game_sys/core/experience_functions.py
"""
Experience and Leveling System for RPG Game.
This module handles experience accumulation and level-ups.
"""
from logs.logs import get_logger
from typing import Any
# Import character and item classes for isinstance checks


log = get_logger(__name__)


class Levels:
    """
    Manages a thing’s level and experience.
    If the thing has a `gain_experience` method (i.e. Player), defer to it.
    """

    def __init__(
        self,
        thing: Any,
        level: int = 1,
        experience: int = 0,
        max_level: int = 100,
    ) -> None:
        self.thing: Any = thing
        self.max_level: int = max_level
        self._lvl: int = 1
        self._experience: int = 0
        self.lvl = level
        self.experience = experience

    def __str__(self) -> str:
        return (
            f"Name: {self.thing.name}\n"
            f"Level: {self.lvl} Experience: {self.experience}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def add_experience(self, exp: int) -> None:
        """
        Add experience points, and level up if thresholds are reached.
        If `self.thing` has `gain_experience`, defer to that method.
        """
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")

        self.experience += exp

        if hasattr(self.thing, "gain_experience"):
            # Delegate leveling logic to the thing
            return

        # NPC/Enemy: auto-level up here
        while (self.lvl < self.max_level and
               self.experience >= self.required_experience()):
            self.level_up()

    def remove_experience(self, exp: int) -> None:
        """Remove experience points from the thing (floors at zero)."""
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")
        self.experience = max(0, self.experience - exp)
        log.info(f"{self.thing.name} lost {exp} experience points.")

    def level_up(self) -> None:
        """
        Internal level-up: deduct needed XP, bump level,
        and perform character-specific actions like
        recalc stats, restore resources.
        """
        to_next = self.required_experience()
        self.experience -= to_next
        self.lvl += 1

        # Character-specific hooks
        from game_sys.character.actor import Actor
        from game_sys.items.item_base import Item
        if isinstance(self.thing, Actor):
            try:
                self.thing.update_stats()
                self.thing.restore_all()
            except AttributeError:
                pass
        # Item rescaling on level change
        elif isinstance(self.thing, Item):
            try:
                self.thing.rescale(self.lvl)
            except AttributeError:
                pass
        from game_sys.core.hooks import hook_dispatcher
        hook_dispatcher.fire(
            "character.level_up",
            character=self.thing,
            new_level=self.thing.levels.lvl
            )
        log.info(f"{self.thing.name} reached level {self.lvl}!")

    def change_level(self, new_level: int) -> None:
        """Force-set the thing's level (with validation)."""
        if not isinstance(new_level, int):
            raise TypeError("Level must be an integer.")
        self.lvl = new_level
        log.info(f"{self.thing.name} level changed to {self.lvl}.")

    def reset_experience(self) -> None:
        """Reset XP to zero."""
        self.experience = 0
        log.info("Experience reset to zero.")

    def reset_level(self) -> None:
        """Reset level to 1."""
        self.lvl = 1
        log.info("Level reset to 1.")

    def reset(self) -> None:
        """Reset both level and experience."""
        self.reset_experience()
        self.reset_level()
        log.info("Experience and level have been reset.")

    def gain_from(self, enemy: Any) -> None:
        """
        Gain XP from an enemy if it has an 'exp_value' attribute.
        """
        reward = getattr(enemy, "exp_value", None)
        if reward is None:
            return
        self.add_experience(reward)

    def required_experience(self) -> int:
        """
        XP needed to reach the next level. Formula: 100*lvl^2 + 100*lvl.
        """
        if self.lvl >= self.max_level:
            return float("inf")
        return 100 * self.lvl ** 2 + 100 * self.lvl

    @property
    def experience(self) -> int:
        return self._experience

    @experience.setter
    def experience(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Experience must be an integer.")
        self._experience = max(0, value)

    @property
    def lvl(self) -> int:
        return self._lvl

    @lvl.setter
    def lvl(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Level must be an integer.")
        self._lvl = max(1, min(value, self.max_level))
