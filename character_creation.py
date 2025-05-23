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
        # Display character stats and inventory
        return (f"{self.__class__.__name__}:\n" #Shows the Class of the character
                f"{self.lvls}\n" #Shows the level and experience of the character
                f"Class: {self.job.job}\n" #Shows the character class 
                f"{'-'*10}\n"
                f"Attack: {self.attack} (+{self._equipment_bonus.attack})\n" #Base stats + bonus stats
                f"Defense: {self.defense} (+{self._equipment_bonus.defense})\n"
                f"Speed: {self.speed} (+{self._equipment_bonus.speed})\n"
                f"Health: {self.health} (+{self._equipment_bonus.health})\n"
                f"Mana: {self.mana} (+{self._equipment_bonus.mana})\n"
                f"Stamina: {self.stamina} (+{self._equipment_bonus.stamina})\n"
                f"{'-'*10}\n"
                f"{self.inventory}") #Shows the inventory of the character
        #Inventory shows the items in the inventory and their stats
    def __repr__(self) -> str:
        """String representation of the character for debugging."""
        # Display character stats and inventory in a more compact format
        return (f"{self.__class__.__name__}") + \
               (f"name={self.name}, lvl={self.lvl}, attack={self.attack}, defense={self.defense}, ") + \
               (f"speed={self.speed}, health={self.health}, mana={self.mana}, ") + \
               (f"stamina={self.stamina}, inventory={self.inventory}")    
    def __eq__(self, other) -> bool:
        """Check if two characters are equal based on their name and level."""
        if not isinstance(other, Character):
            return NotImplemented
        return self.name == other.name and self.lvl == other.lvl
    def get_stats(self) -> Stats:
        """Get the effective stats of the character."""
        return self._effective_stats
    def update_stats(self) -> None:
            """Update the character's stats based on the current level and class."""
            self._equipment_bonus = Stats(
                attack=sum(getattr(item, "attack_power", 0) for item in self.inventory.equipped_items.values() if item),
                defense=sum(getattr(item, "defense_power", 0) for item in self.inventory.equipped_items.values() if item),
                speed=sum(getattr(item, "speed_power", 0) for item in self.inventory.equipped_items.values() if item),
                health=sum(getattr(item, "health_power", 0) for item in self.inventory.equipped_items.values() if item),
                mana=sum(getattr(item, "mana_power", 0) for item in self.inventory.equipped_items.values() if item),
                stamina=sum(getattr(item, "stamina_power", 0) for item in self.inventory.equipped_items.values() if item),
                max_health=sum(getattr(item, "health_power", 0) for item in self.inventory.equipped_items.values() if item),
                max_mana=sum(getattr(item, "mana_power", 0) for item in self.inventory.equipped_items.values() if item),
                max_stamina=sum(getattr(item, "stamina_power", 0) for item in self.inventory.equipped_items.values() if item),
            )
            self._effective_stats = self._base_stats + self._equipment_bonus
            self.update_max_caps()
    def update_max_caps(self):
        """Update the maximum caps for health, mana, and stamina."""
        # Directly read from effective stats' max_* fields
        self._base_stats.max_health = self._effective_stats.max_health
        self._base_stats.max_mana = self._effective_stats.max_mana
        self._base_stats.max_stamina = self._effective_stats.max_stamina
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
            "inventory": [item.to_dict() for item in self.inventory.get_items()],
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
    def take_damage(self, amount: int):
        """Reduce the character's health by the specified amount."""
        self._base_stats.health = max(0, self._base_stats.health - amount)
        self.update_stats()

    def drain_mana(self, amount: int):
        """Reduce the character's mana by the specified amount."""
        self._base_stats.mana = max(0, self._base_stats.mana - amount)
        self.update_stats()

    def drain_stamina(self, amount: int):
        """Reduce the character's stamina by the specified amount."""
        self._base_stats.stamina = max(0, self._base_stats.stamina - amount)
        self.update_stats()


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
    def __init__(self, name: str = "Enemy", level: int = 1) -> None:
        super().__init__(name, level)
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
    def __init__(self, name: str = "Hero", level: int = 1)  -> None:
        super().__init__(name, level)
        """Initialize the player with default stats and an empty inventory."""