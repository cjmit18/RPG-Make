# game_sys/core/experience_functions.py

"""
Experience and Leveling System for RPG Game.
This module handles experience accumulation and level-ups.
(No import of LearningSystem here—that belongs in Player.)
"""

from logs.logs import get_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_sys.character.character_creation import Character

log = get_logger(__name__)


class Levels:
    """
    Manages a character’s level and experience.
    If the Character has a `gain_experience` method (i.e. Player), defer to it
    so that Player can award skill points. Otherwise, auto-level up here.
    """

    def __init__(
        self,
        character: "Character",
        level: int = 1,
        experience: int = 0,
        max_level: int = 100,
    ) -> None:
        self.character: "Character" = character
        self.max_level: int = max_level
        self._lvl: int = 1
        self._experience: int = 0

        self.lvl = level
        self.experience = experience

    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.lvl} Experience: {self.experience}"

    def __repr__(self) -> str:
        return self.__str__()

    def add_experience(self, exp: int) -> None:
        """
        Add experience points, and level up if thresholds are reached.
        If `self.character` has `gain_experience`, return immediately so that
        Player.gain_experience handles the leveling (and skill points).
        """
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")

        self.experience += exp

        if hasattr(self.character, "gain_experience"):
            # Defer leveling (and awarding SP) to Player.gain_experience
            return

        # NPC/Enemy: auto-level up here
        while self.lvl < self.max_level and self.experience >= self.required_experience():
            self.level_up()

    def remove_experience(self, exp: int) -> None:
        """Remove experience points from the character (floors at zero)."""
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")
        self.experience = max(0, self.experience - exp)
        log.info(f"{self.character.name} lost {exp} experience points.")

    def level_up(self) -> None:
        """Internal level-up: deduct needed XP, bump level, recalc stats, restore resources."""
        to_next = self.required_experience()
        self.experience -= to_next
        self.lvl += 1

        try:
            self.character.update_stats()
            self.character.restore_all()
        except AttributeError:
            # Some subclasses may not implement update_stats/restore_all
            pass

        log.info(f"{self.character.name} reached level {self.lvl}!")

    def change_level(self, new_level: int) -> None:
        """Force‐set the character’s level (with validation)."""
        if not isinstance(new_level, int):
            raise TypeError("Level must be an integer.")
        self._lvl = max(1, min(new_level, self.max_level))
        log.info(f"{self.character.name} level changed to {self._lvl}.")

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

    def gain_from(self, enemy: object) -> None:
        """
        If `enemy` has an `exp_value` attribute, gain that much XP.
        Otherwise do nothing.
        """
        reward = getattr(enemy, "exp_value", None)
        if reward is None:
            return
        self.add_experience(reward)

    def required_experience(self) -> int:
        """
        XP needed to reach the next level. Example formula: 100*lvl^2 + 100*lvl.
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
