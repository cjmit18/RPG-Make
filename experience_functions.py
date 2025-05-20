"""Experience and Leveling System for RPG Game
This module handles the experience and leveling system for characters in the game."""
import combat_functions
import character_creation
import logging
log = logging.getLogger(__name__)
class Levels:
    """Class to manage character levels and experience points."""
    def __init__(self, character, level=1, experience=0):
        self.character: character_creation.class_creation = character
        self._lvl: int = level
        self._experience: int = experience
    def __str__(self):
        return f"Name: {self.character.name}\nLevel: {self.lvl} Experience: {self.experience}"
    def __repr__(self):
        return f"Name: {self.character.name}\nLevel: {self.lvl} Experience: {self.experience}"

    def add_experience(self, exp: int) -> None:
        """Add experience points to the character."""
        if not isinstance(exp, int):
            raise TypeError("Experience must be an integer.")
        else:
            self.experience += exp
        if self.experience >= self.required_experience() and not isinstance(self.character, character_creation.Enemy):
            self.level_up()
    def level_up(self) -> None:
        """Level up the character if enough experience is gained."""
        while self.experience >= self.required_experience():
            self.experience -= self.required_experience()
            self.lvl += 1
            self.character.update_stats()
            log.info(f"{self.character.name} leveled up to level {self.lvl}!")
    def required_experience(self) -> int:
        """Calculate the required experience points for the next level."""
        return (self.lvl * 100) * 2
    def change_level(self, new_level) -> None:
        """Change the character's level."""
        if new_level < 1:
            raise ValueError("Level must be at least 1.")
        self.lvl = new_level
        log.info(f"Level changed to {self.lvl}.")
    def reset_experience(self) -> None:
        """Reset the character's experience points."""
        self.experience: int = 0
        log.info("Experience points have been reset.")
    def reset_level(self) -> None:
        """Reset the character's level to 1."""
        self.lvl; int = 1
        log.info("Level has been reset to 1.")
    def reset(self) -> None:
        """Reset both experience and level."""
        self.reset_experience()
        self.reset_level()
        log.info("Experience and level have been reset.")
    def experience_calc(self, enemy) -> None:
        """Calculate experience gained from defeating an enemy."""
        self.add_experience(enemy.lvls.experience)
    @property
    def experience(self):
        if self.character.__class__ == character_creation.Enemy and self._experience <= 0:
            self._experience += self._lvl * 100
            return self._experience
        else:
            return self._experience
    @experience.setter
    def experience(self, experience):
        if not isinstance(experience, int):
            raise TypeError("Experience must be an integer.")
        elif experience < 0:
            self._experience = 0
        else:
            self._experience = experience
    @property
    def lvl(self):
        return self._lvl
    @lvl.setter
    def lvl(self, lvl):
        if not isinstance(lvl, int):
            raise TypeError("Level must be an integer.")
        elif lvl < 0:
            self._lvl = 0
        else:
            self._lvl = lvl
    