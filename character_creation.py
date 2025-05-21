"""Character Creation Module
This module contains the Character class and its subclasses (NPC, Enemy, Player) for a game."""
import inventory_functions
import experience_functions
import class_creation
import items_list
import potion_list as potions
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
        self.name: str = name #Name of the character  
        #Base stats generaated based on the level  
        self._attack: int = 0
        self._defense: int = 0
        self._speed: int = 0
        self._health: int = 0
        self._mana: int = 0
        self._stamina: int = 0
        self.lvls: experience_functions.Levels = experience_functions.Levels(self, level, experience)
        #Levels component handles experience and leveling up
        self.inventory: inventory_functions.Inventory = inventory_functions.Inventory(self)
        #Inventory component handles item management and equipment
        self.class_: class_creation.Base = class_creation.Base(self)
        #Class component handles character class and its effects
        self.update_stats()
        #Update stats based on the current level and class
        #Initialize the character with default stats and an empty inventory
    def __str__(self) -> str:
        """String representation of the character."""
        # Display character stats and inventory
        return (f"{self.__class__.__name__}:\n" #Shows the Class of the character
                f"{self.lvls}\n" #Shows the level and experience of the character
                f"Class: {self.class_.class_}\n" #Shows the character class 
                f"{'-'*10}\n"
                f"Attack: {self.attack} (+{self._get_total_bonus('attack')})\n" #Base stats + bonus stats
                f"Defense: {self.defense} +({self._get_total_bonus('defense')})\n"
                f"Speed: {self.speed} (+{self._get_total_bonus('speed')})\n"
                f"Health: {self.health} (+{self._get_total_bonus('health')})\n"
                f"Mana: {self.mana} (+{self._get_total_bonus('mana')})\n"
                f"Stamina: {self.stamina} (+{self._get_total_bonus('stamina')})\n"
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
        """Equality check for comparing two characters."""
        # Compare character attributes for equality
        if isinstance(other, Character):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def _get_total_bonus(self, stat_name: str) -> int:
        return sum(
            getattr(item, f"{stat_name}_power", 0)
            for item in self.inventory.equipped_items.values()
            if item
        )
    def update_stats(self) -> None:
        """Add equipment bonuses on top of class-defined base stats."""
        for stat in ["attack", "defense", "speed", "health", "mana", "stamina"]:
            base_value = getattr(self, stat)  # class-defined stat (e.g., from Knight)
            equipment_bonus = sum(
                getattr(item, f"{stat}_power", 0)
                for item in self.inventory.equipped_items.values()
                if item
            )
            setattr(self, f"_{stat}", base_value + equipment_bonus)

        log.debug(f"{self.name} stats updated: {self.__dict__}")
    def change_class(self, class_):
        """Change the character's class and update stats accordingly."""
        self.class_: class_creation.Base = class_(self) 
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
        self.lvls.lvl = lvl
        self.update_stats() #Update stats when level changes
    #----Properties for public access----
    #----Attack----
    @property
    def attack(self) -> int:
        """Calculate the total attack value."""
        return self._attack
    @attack.setter
    def attack(self, attack) -> None:
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        self._attack: int = max(0, attack)
    #----Defense----
    @property
    def defense(self) -> int:
        return self._defense
    @defense.setter
    def defense(self, defense) -> None:
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        self._defense: int = max(0, defense)
    #----Speed----
 
    @property
    def speed(self) -> int:
        """Calculate the total speed value."""
        return self._speed
    @speed.setter
    def speed(self, speed) -> None:
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        self._speed: int = max(0, speed)
    #----Health----
    @property
    def health(self) -> int:
        return self._health
    @health.setter
    def health(self, health) -> None:
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        self._health: int = max(0, health)
    #----Mana----
    @property
    def mana(self) -> int:
        return self._mana
    @mana.setter
    def mana(self, mana) -> None:
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        self._mana: int = max(0, mana)
    #----Stamina----
    @property
    def stamina(self) -> int:
        return self._stamina
    @stamina.setter
    def stamina(self, stamina) -> None:
        if not isinstance(stamina, int):
            raise TypeError("Stamina must be an integer.")
        self._stamina: int = max(0, stamina)
        #----Inventory and Class----
    #----Inventory----
    @property
    def inventory(self): 
        return self._inventory
    @inventory.setter
    def inventory(self, inventory) -> None:
        if not isinstance(inventory, inventory_functions.Inventory):
            raise TypeError("Inventory must be an Inventory object.")
        self._inventory: inventory_functions.Inventory = inventory

    #----Class----
    @property
    def class_(self) -> class_creation.Base:
        return self._class_
    @class_.setter
    def class_(self, class_) -> None:
        if not isinstance(class_, class_creation.Base):
            raise TypeError("Class must be a Base object.")
        self._class_: class_creation.Base = class_
        
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
        potion = potions.Health_Potion(lvl=level)
        self.inventory.add_item(potion, gen.generate_random_number(1, 5))
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