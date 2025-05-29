
"""Character Creation Module
This module contains the Character class and its subclasses (NPC, Enemy, Player) for a game."""
from game_sys.core.actor import Actor
from game_sys.jobs import Base

class Character(Actor):
    """Base class for all characters in the game."""
    def __init__(self, name: str = "Template", level: int = 1, experience: int = 0):
        # pass Base as the job_class so job modifiers & starting items still apply
        super().__init__(name, level, experience, job_class=Base)
    def __str__(self) -> str:
        eff = self.stats.effective()
        lines = [
            f"{self.__class__.__name__}: {self.name}",
            f"Level: {self.levels.lvl} Experience: {self.levels.experience}",
            f"Class: {self.job.__class__.__name__ if self.job.__class__.__name__ != 'Job' else 'None'}",
            "-" * 20,
        ]
        for stat in ("attack", "defense", "speed", "health", "mana", "stamina"):
            val = eff.get(stat, 0)
            if stat in ("health", "mana", "stamina"):
                cur = getattr(self, f"current_{stat}", 0)
                lines.append(f"{stat.capitalize()}: {cur}/{val}")
            else:
                lines.append(f"{stat.capitalize()}: {val}")
        lines.append("-" * 20)
        lines.append(str(self.inventory))
        return "\n".join(lines)
class NPC(Character):
    """Non-Playable Character class."""
    # NPCs can have custom names and levels, but no experience
    def __init__(self, name: str = "NPC", level: int = 1) -> None:
        super().__init__(name, level)
class Enemy(Character):
    """Enemy class for combat encounters."""
    def __init__(
        self,
        name: str = "Enemy",
        level: int = 1,
        experience: int = 0
    ) -> None:
        # Pass the experience through so Enemy can start with a custom XP
        super().__init__(name, level, experience)
        # By default, enemies yield "level * 100" XP unless overridden
        if experience == 0:
            self.levels.experience = self.levels.lvl * 100

class Player(Character):
    """Player class for the main character."""
    def __init__(self, name: str = "Hero", level: int = 1, experience: int = 0) -> None:
        super().__init__(name, level, experience)
        # Player-specific initialization (e.g., UI hooks) can go here
