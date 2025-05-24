"""Character Creation Module
This module contains the Character class and its subclasses (NPC, Enemy, Player) for a game."""
from inventory_functions import Inventory
from class_creation import Base
from stats import Stats
import experience_functions 
import gen
import logging
log = logging.getLogger(__name__)
class Character():
    """
    Base class for all characters in the game.
    Attributes:
        name (str): Name of the character.
        attack (int): Attack power of the character.
        defense (int): Defense power of the character.
        speed (int): Speed of the character.
        health (int): Health points of the character.
        mana (int): Mana points of the character.
        stamina (int): Stamina points of the character.
        lvl (int): Level of the character.
        experience (int): Experience points of the character.
        inventory (Inventory): Inventory object for managing items.
    """
    def __init__(self, name: str = "Template", level: int = 1, experience: int = 0) -> None:
        # Initialize the character with default stats and an empty inventory.
        """Initialize the character with default stats and an empty inventory.
        Args:
            name (str): Name of the character.
            level (int): Level of the character.
            experience (int): Experience points of the character.
        """
        # Set default values for character attributes
        self._name: str = name
        #Name of the character  
        self.lvls: experience_functions.Levels = experience_functions.Levels(self, level, experience)
        #Levels component handles experience and leveling up
        self._base_stats: Stats = Stats()
        #Base stats component handles the base stats of the character
        self._equipment_bonus: Stats = Stats()
        #Equipment bonus component handles the bonus stats from equipped items
        self._effective_stats: Stats = self._base_stats + self._equipment_bonus
        #Effective stats component handles the effective stats of the character
        self.inventory: Inventory = Inventory(self)
        self.job: Base = Base(self)
        #Class component handles character class and its effects

        #Update stats based on the current level and class
        #Initialize the character with default stats and an empty inventory
        self.update_stats()
    def __str__(self) -> str:
        """String representation of the character."""
        # Display character stats and inventory in a more compact format
        lines = [
            f"{self.__class__.__name__}:",
            f"{self.lvls}",
            f"Class: {self.job.job}",
            "-" * 10
        ]

        # Current stats with gear bonus
        for stat in ["attack", "defense", "speed", "health", "mana", "stamina"]:
            base = getattr(self._base_stats, stat)
            bonus = getattr(self._equipment_bonus, stat)
            total = base + bonus
            if bonus:
                lines.append(f"{stat.capitalize()}: {total} (+{bonus})")
            else:
                lines.append(f"{stat.capitalize()}: {total}")

        # Max caps only if bonus or base is > 0
        for max_stat in ["max_health", "max_mana", "max_stamina"]:
            base = getattr(self._base_stats, max_stat, 0)
            bonus = getattr(self._equipment_bonus, max_stat, 0)
            total = base + bonus
            if base or bonus:
                if bonus:
                    lines.append(f"{max_stat.replace('_', ' ').capitalize()}: {total} (+{bonus})")
                else:
                    lines.append(f"{max_stat.replace('_', ' ').capitalize()}: {total}")

        lines.append("-" * 10)
        lines.append(str(self.inventory))
        return {'\n'.join(lines)}
    def __repr__(self) -> str:
        """String representation of the character for debugging and interactive display."""
        return self.__str__()
    def __eq__(self, other) -> bool:
        """Check if two characters are equal based on their name and level."""
        if not isinstance(other, Character):
            return NotImplemented
        return self.name == other.name and self.lvl == other.lvl
    def get_stats(self) -> Stats:
        """Get the effective stats of the character."""
        return self._effective_stats
    def update_stats(self) -> None:
        """Update the character's effective stats based on base and equipment bonuses."""
        equipped = self.inventory.equipped_items.values()

        self._equipment_bonus = Stats(
            attack=sum(getattr(item, "attack_power", 0) for item in equipped if item),
            defense=sum(getattr(item, "defense_power", 0) for item in equipped if item),
            speed=sum(getattr(item, "speed_power", 0) for item in equipped if item),
            health=0,  # Do not add item health to current health
            mana=0,    # Prevent bonus mana from doubling
            stamina=0, # Prevent bonus stamina from doubling
            max_health=sum(getattr(item, "health_power", 0) for item in equipped if item),
            max_mana=sum(getattr(item, "mana_power", 0) for item in equipped if item),
            max_stamina=sum(getattr(item, "stamina_power", 0) for item in equipped if item),
        )
        self._effective_stats = self._base_stats + self._equipment_bonus
        self.clamp_current_stats()
        # Clamp the current stats to their maximum values
    def clamp_current_stats(self):
            """Clamp the current stats to their maximum values."""
            health_cap = self._effective_stats.max_health
            mana_cap = self._effective_stats.max_mana
            stamina_cap = self._effective_stats.max_stamina
            self._base_stats.health = min(self._base_stats.health, health_cap)
            self._base_stats.mana = min(self._base_stats.mana, mana_cap)
            self._base_stats.stamina = min(self._base_stats.stamina, stamina_cap)
    def use_item(self, item):
        """Use an item from the inventory."""
        return self.inventory.use_item(item)
    def change_class(self, job):
        """Change the character's class and update stats accordingly."""
        self.job: Base = job(self) 
        self.update_stats()
    def get_stat_breakdown(self, stat_name: str) -> str:
        """Get a detailed breakdown of a specific stat."""
        base = getattr(self._base_stats, stat_name)
        bonus = getattr(self._equipment_bonus, stat_name)
        return f"{stat_name.capitalize()}: {base + bonus} (Base: {base} + Gear: {bonus})"
    def to_dict(self) -> dict:
        """Convert the character to a dictionary representation."""
        # Convert the character's attributes to a dictionary
        return {
            "name": self.name,
            "level": self.lvls.lvl,
            "experience": self.lvls.experience,
            "class": self.job.__class__.__name__,
            "inventory": [item.to_dict() for item in self.inventory.items],
            "equipped": {slot: item.to_dict() for slot, item in self.inventory.equipped_items.items() if item}
        }
    @classmethod
    def from_dict(cls, data: dict, item_loader) -> "Character":
        """Create a character from a dictionary representation."""
        # Load the character's class based on the saved data
        from class_creation import Knight, Mage, Rogue, Healer, Base
        CLASS_MAP = {
            "Knight": Knight,
            "Mage": Mage,
            "Rogue": Rogue,
            "Healer": Healer,
            "Base": Base
        }
        char = cls(name=data["name"], level=data["level"], experience=data["experience"])
        job_class = CLASS_MAP.get(data.get("class", "Base"), Base)
        char.change_class(job_class)

        # Load inventory
        for item_data in data.get("inventory", []):
            item = item_loader(item_data)
            char.inventory.add_item(item)

        # Equip items
        for slot, item_data in data.get("equipped", {}).items():
            item = item_loader(item_data)
            char.inventory.equip_item(item)
        return char
    def take_damage(self, amount: int) -> None:
        """Reduce the character's health by the specified amount."""
        self._base_stats.health = max(self._base_stats.health - amount)
        self.clamp_current_stats()

    def drain_mana(self, amount: int) -> None:
        """Reduce the character's mana by the specified amount."""
        self._base_stats.mana = max(self._base_stats.mana - amount)
        self.clamp_current_stats()

    def drain_stamina(self, amount: int) -> None:
        """Reduce the character's stamina by the specified amount."""
        self._base_stats.stamina = max(self._base_stats.stamina - amount)
        self.clamp_current_stats()
    def heal(self, amount: int) -> None:
        """Heal the character by the specified amount."""
        self._base_stats.health  += amount
        self.clamp_current_stats()


    #----Name And Level Properties----
    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.") 
        self._name: str = name
   #---Level----
    @property
    def lvl(self) -> int:
        return self.lvls.lvl
    @lvl.setter
    def lvl(self, lvl) -> None:
        if lvl < self.lvls.lvl:
            raise ValueError("Level cannot be decreased.")
        if lvl > self.lvls.max_level:
            lvl = self.lvls.max_level
        self.lvls.lvl = lvl
        self.update_stats() #Update stats when level changes
    #----Properties for public access----
    #----Attack----
    @property
    def attack(self) -> int:
        """Calculate the total attack value."""
        return self._effective_stats.attack
    @attack.setter
    def attack(self, attack) -> None:
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        self._base_stats.attack = max(0, attack)
    #----Defense----
    @property
    def defense(self) -> int:
        return self._effective_stats.defense
    @defense.setter
    def defense(self, defense) -> None:
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        self._base_stats.defense = max(0, defense)
    #----Speed----
 
    @property
    def speed(self) -> int:
        """Calculate the total speed value."""
        return self._effective_stats.speed
    @speed.setter
    def speed(self, speed) -> None:
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        self._base_stats.speed = max(0, speed)
    #----Health----
    @property
    def max_health(self):
        return self._effective_stats.max_health
    @property
    def health(self) -> int:
        return self._effective_stats.health
    @health.setter
    def health(self, health) -> None:
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        cap = self.max_health if self.max_health > 0 else 9999
        self._base_stats.health = min(max(0, health), cap)
    #----Mana----
    @property
    def max_mana(self):
        return self._effective_stats.max_mana
    @property
    def mana(self) -> int:
        return self._effective_stats.mana
    @mana.setter
    def mana(self, mana) -> None:
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        cap = self.max_mana if self.max_mana > 0 else 9999
        self._base_stats.mana = min(max(0, mana), cap)
    #----Stamina----
    @property
    def max_stamina(self):
        return self._effective_stats.max_stamina
    @property
    def stamina(self) -> int:
        return self._effective_stats.stamina
    @stamina.setter
    def stamina(self, stamina) -> None:
        if not isinstance(stamina, int):
            raise TypeError("Stamina must be an integer.")
        cap = self.max_stamina if self.max_stamina > 0 else 9999
        self._base_stats.stamina = min(max(0, stamina), cap)
        #----Inventory and Class----
    #----Inventory----
    @property
    def inventory(self): 
        return self._inventory
    @inventory.setter
    def inventory(self, inventory) -> None:
        if not isinstance(inventory, Inventory):
            raise TypeError("Inventory must be an Inventory object.")
        self._inventory: Inventory = inventory

    #----Class----
    @property
    def job(self) -> Base:
        return self._job
    @job.setter
    def job(self, job) -> None:
        if not isinstance(job, Base):
            raise TypeError("Class must be a Base object.")
        self._job: Base = job
        
class NPC(Character):
    """
    Non-Playable Character (NPC) class representing characters that are not controlled by the player."""
    # Inherits from the Character class.
    def __init__(self, name: str = "NPC", level: int = 1) -> None:
        super().__init__(name, level)
class Enemy(Character):
    """
    Enemy class representing hostile characters in the game.
    Attributes:
        name (str): Name of the enemy.
        level (int): Level of the enemy.
        inventory (Inventory): Inventory object for managing items.
    """
    def __init__(self, name: str = "Enemy", level: int = 1, experience: int = 0) -> None:
        super().__init__(name, level, experience)
        # Add a health potion to the enemy's inventory
class Player(Character):
    """
    Player class representing the main character in the game.
    Inherits from the Character class.
    Attributes:
        name (str): Name of the player.
        level (int): Level of the player.
        inventory (Inventory): Inventory object for managing items.
    """
    def __init__(self, name: str = "Hero", level: int = 1, experience: int = 0)  -> None:
        super().__init__(name, level, experience)
        """Initialize the player with default stats and an empty inventory."""