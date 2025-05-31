"""Experience and Leveling System for RPG Game
This module handles the experience and leveling system for characters in the game."""
from logs.logs import get_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_sys.character.character_creation import Character

log = get_logger(__name__)


class Levels:
    """Class to manage character levels and experience points."""
    def __init__(
        self,
        character: "Character",
        level: int = 1,
        experience: int = 0,
        max_level: int = 100,
    ) -> None:
        self.character: "Character" = character
        self.max_level: int = max_level
        self._lvl: int = level
        self._experience: int = 0
        # Use setters for validation and callbacks
        self.lvl = level
        self.experience = experience

    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.lvl} Experience: {self.experience}"

    def __repr__(self) -> str:
        return self.__str__()

    def add_experience(self, exp: int) -> None:
        from game_sys.character.character_creation import Enemy
        """Add experience and level up if threshold reached."""
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")
        self.experience += exp
        # Roll over XP into levels
        if not isinstance(self.character, Enemy):
            while self.lvl < self.max_level and self.experience >= self.required_experience():
                self.level_up()
    def remove_experience(self, exp: int) -> None:
        """Remove experience points from the character."""
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")
        self.experience = max(0, self.experience - exp)
        log.info(f"{self.character.name} lost {exp} experience points.")

    def level_up(self) -> None:
        """Level up the character when enough experience is gained."""
        self.experience -= self.required_experience()
        self.lvl += 1
        # Reset and reapply stats
        try:
            self.character.update_stats()
            self.character.restore_all()
        except AttributeError:
            pass
        log.info(f"{self.character.name} reached level {self.lvl}!")

    def change_level(self, new_level: int) -> None:
        """Change the character's level directly."""
        if not isinstance(new_level, int):
            raise TypeError("Level must be an integer.")
        if new_level < 1:
            raise ValueError("Level must be at least 1.")
        self.lvl = min(new_level, self.max_level)
        log.info(f"Level changed to {self.lvl}.")

    def reset_experience(self) -> None:
        """Reset the character's experience points to zero."""
        self.experience = 0
        log.info("Experience points have been reset.")

    def reset_level(self) -> None:
        """Reset the character's level to 1."""
        self.lvl = 1
        log.info("Level has been reset to 1.")

    def reset(self) -> None:
        """Reset both level and experience."""
        self.reset_experience()
        self.reset_level()
        log.info("Experience and level have been reset.")

    def gain_from(self, enemy) -> None:
        """Gain experience based on enemy's XP value."""
        try:
            reward = enemy.lvls.experience
        except AttributeError:
            reward = int(enemy.lvls.required_experience)
        self.add_experience(reward)
    def required_experience(self) -> int:
        """Total experience needed to reach the next level."""
        if self.lvl >= self.max_level:
            return float('inf')
        return 100 * self.lvl**2 + 100 * self.lvl

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
        """Current level of the character."""
        return self._lvl

    @lvl.setter
    def lvl(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Level must be an integer.")
        self._lvl = max(1, min(value, self.max_level))