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
                f"Attack: {self.attack} ({self.get_attack_bonus})\n" #Base stats + bonus stats
                f"Defense: {self.defense} ({self.get_defense_bonus})\n" 
                f"Speed: {self.speed} ({self.get_speed_bonus})\n"
                f"Health: {self.health} ({self.get_health_bonus})\n"
                f"Mana: {self.mana} ({self.get_mana_bonus})\n"
                f"Stamina: {self.stamina} ({self.get_stamina_bonus})\n"
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
    def update_stats(self) -> None:
        """Update the character's stats based on the current level and class.
        This method is called whenever the character's level or class changes.
        """
        # Default stat calculation, override in subclasses if needed
        lvl = self.lvls.lvl - 1

        base = {
            "attack": 10 + lvl,
            "defense": 5 + lvl,
            "speed": 10 + lvl,
            "health": 100 + lvl,
            "mana": 100 + lvl,
            "stamina": 100 + lvl
        }
        class_bonuses = {stat: getattr(self.class_, stat, 0) for stat in base}
        equipped_bonuses = {}
        for stat in base:
            total = 0
            for item in self.inventory.equipped_items.values():
                if item:
                    # Check if the item has the stat attribute
                    total += getattr(item, f"{stat}_power", 0)
            equipped_bonuses[stat] = total
        # Calculate final stats
        for stat in base:
            # Set the final stat value
            setattr(self, f"_{stat}", base[stat] + class_bonuses[stat] + equipped_bonuses[stat])
        # Set the final stat value
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
    #Attack is a property that handles the attack of the character
    #It is a property to keep the code clean and organized
    @property
    def get_attack_bonus(self) -> int:
        """Total attack value with bonuses."""
        return self.attack - self.base_attack
    @property
    def base_attack(self) -> int:
        """Base attack value without bonuses."""
        lvl = self.lvls.lvl - 1
        return 10 + lvl
    @property
    def class_bonuses(self) -> int:
        """Class bonuses to attack."""
        return getattr(self.class_, "attack", 0)
    @property
    def equipment_bonuses(self) -> int:
        """Equipment bonuses to attack."""
        total = 0
        for item in self.inventory.equipped_items.values():
            if item:
                # Check if the item has the attack_power attribute
                total += getattr(item, "attack_power", 0)
        return total
    @property
    def attack(self) -> int:
        """Calculate the total attack value."""
        return self.base_attack + self.class_bonuses + self.equipment_bonuses

    @attack.setter
    def attack(self, attack):
        """Set the attack value directly."""
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        self._attack: int = max(0, attack)
    #----Defense----
    #Defense is a property that handles the defense of the character
    #It is a property to keep the code clean and organized
    @property
    def get_defense_bonus(self) -> int:
        """Total defense value with bonuses."""
        return self.defense - self.base_defense
    @property
    def base_defense(self) -> int:
        """Base defense value without bonuses."""
        lvl = self.lvls.lvl - 1
        return 5 + lvl
    @property
    def class_defense_bonuses(self) -> int:
        """Class bonuses to defense."""
        return getattr(self.class_, "defense", 0)
    @property
    def equipment_defense_bonuses(self) -> int:
        """Equipment bonuses to defense."""
        total = 0
        for item in self.inventory.equipped_items.values():
            if item:
                # Check if the item has the defense_power attribute
                total += getattr(item, "defense_power", 0)
        return total
    @property
    def defense(self) -> int:
        return self.base_defense + self.class_defense_bonuses + self.equipment_defense_bonuses
    @defense.setter
    def defense(self, defense) -> None:
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        self._defense: int = max(0, defense)
    #----Speed----
    #Speed is a property that handles the speed of the character
    #It is a property to keep the code clean and organized
    @property
    def get_speed_bonus(self) -> int:
        """Total speed value with bonuses."""
        return self.speed - self.base_speed
    @property
    def base_speed(self) -> int:
        """Base speed value without bonuses."""
        lvl = self.lvls.lvl - 1
        return 10 + lvl
    @property
    def class_speed_bonuses(self) -> int:
        """Class bonuses to speed."""
        return getattr(self.class_, "speed", 0)
    @property
    def equipment_speed_bonuses(self) -> int:
        """Equipment bonuses to speed."""
        total = 0
        for item in self.inventory.equipped_items.values():
            if item:
                # Check if the item has the speed_power attribute
                total += getattr(item, "speed_power", 0)
        return total
    @property
    def speed(self) -> int:
        """Calculate the total speed value."""
        return self.base_speed + self.class_speed_bonuses + self.equipment_speed_bonuses
    @speed.setter
    def speed(self, speed) -> None:
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        self._speed: int = max(0, speed)
    #----Health----
    #Health is a property that handles the health of the character
    #It is a property to keep the code clean and organized
    @property
    def get_health_bonus(self) -> int:
        """Total health value with bonuses."""
        return self.health - self.base_health
    @property
    def base_health(self) -> int:
        """Base health value without bonuses."""
        lvl = self.lvls.lvl - 1
        return 100 + lvl
    @property
    def class_health_bonuses(self) -> int:
        """Class bonuses to health."""
        return getattr(self.class_, "health", 0)
    @property
    def equipment_health_bonuses(self) -> int:
        """Equipment bonuses to health."""
        total = 0
        for item in self.inventory.equipped_items.values():
            if item:
                # Check if the item has the health_power attribute
                total += getattr(item, "health_power", 0)
        return total
    @property
    def health(self) -> int:
        return self. base_health + self.class_health_bonuses + self.equipment_health_bonuses
    #Health is a property that handles the health of the character
    @health.setter
    def health(self, health) -> None:
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        self._health: int = max(0, health)
    #----Mana----
    #Mana is a property that handles the mana of the character
    #It is a property to keep the code clean and organized
    @property
    def get_mana_bonus(self) -> int:
        """Total mana value with bonuses."""
        return self.mana - self.base_mana
    @property
    def base_mana(self) -> int:
        """Base mana value without bonuses."""
        lvl = self.lvls.lvl - 1
        return 100 + lvl
    @property
    def class_mana_bonuses(self) -> int:
        """Class bonuses to mana."""
        return getattr(self.class_, "mana", 0)
    @property
    def equipment_mana_bonuses(self) -> int:
        """Equipment bonuses to mana."""
        total = 0
        for item in self.inventory.equipped_items.values():
            if item:
                # Check if the item has the mana_power attribute
                total += getattr(item, "mana_power", 0)
        return total
    @property
    def mana(self) -> int:
        return self.base_mana + self.class_mana_bonuses + self.equipment_mana_bonuses
    @mana.setter
    def mana(self, mana) -> None:
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        self._mana: int = max(0, mana)
    
    #----Stamina----
    #Stamina is a property that handles the stamina of the character
    #It is a property to keep the code clean and organized
    @property
    def get_stamina_bonus(self) -> int:
        """Total stamina value with bonuses."""
        return self.stamina - self.base_stamina
    @property
    def base_stamina(self) -> int:
        """Base stamina value without bonuses."""
        lvl = self.lvls.lvl - 1
        return 100 + lvl
    @property
    def class_stamina_bonuses(self) -> int:
        """Class bonuses to stamina."""
        return getattr(self.class_, "stamina", 0)
    @property
    def equipment_stamina_bonuses(self) -> int:
        """Equipment bonuses to stamina."""
        total = 0
        for item in self.inventory.equipped_items.values():
            if item:
                # Check if the item has the stamina_power attribute
                total += getattr(item, "stamina_power", 0)
        return total
    @property
    def stamina(self) -> int:
        return self.base_stamina + self.class_stamina_bonuses + self.equipment_stamina_bonuses
    @stamina.setter
    def stamina(self, stamina) -> None:
        if not isinstance(stamina, int):
            raise TypeError("Stamina must be an integer.")
        self._stamina: int = max(0, stamina)
        #----Inventory and Class----
    #----Inventory----
    #Inventory is a class that handles the items and equipment of the character
    #It is a separate class to keep the code clean and organized
    @property
    def inventory(self): 
        return self._inventory
    @inventory.setter
    def inventory(self, inventory) -> None:
        if not isinstance(inventory, inventory_functions.Inventory):
            raise TypeError("Inventory must be an Inventory object.")
        self._inventory: inventory_functions.Inventory = inventory

    #----Class----
    #Class is a class that handles the character class and its effects
    #It is a separate class to keep the code clean and organized
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
    def update_stats(self) -> None:
        """Update the character's stats based on the current level and class.
        This method is called whenever the character's level or class changes.
        """
        # Default stat calculation, override in subclasses if needed
        lvl = self.lvls.lvl - 1

        base = {
            "attack": 10 + lvl,
            "defense": 5 + lvl,
            "speed": 10 + lvl,
            "health": 100 + lvl,
            "mana": 100 + lvl,
            "stamina": 100 + lvl
        }
        class_bonuses = {stat: getattr(self.class_, stat, 0) for stat in base}
        equipped_bonuses = {}
        for stat in base:
            total = 0
            for item in self.inventory.equipped_items.values():
                if item:
                    # Check if the item has the stat attribute
                    total += getattr(item, f"{stat}_power", 0)
            equipped_bonuses[stat] = total
        # Calculate final stats
        for stat in base:
            # Set the final stat value
            setattr(self, f"_{stat}", base[stat] + class_bonuses[stat] + equipped_bonuses[stat])
        # Set the final stat value
        log.debug(f"{self.name} stats updated: {self.__dict__}")
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
    def update_stats(self) -> None:
        """Update the character's stats based on the current level and class.
        This method is called whenever the character's level or class changes.
        """
        # Default stat calculation, override in subclasses if needed
        lvl = self.lvls.lvl - 1

        base = {
            "attack": 10 + lvl,
            "defense": 5 + lvl,
            "speed": 10 + lvl,
            "health": 100 + lvl,
            "mana": 100 + lvl,
            "stamina": 100 + lvl
        }
        class_bonuses = {stat: getattr(self.class_, stat, 0) for stat in base}
        equipped_bonuses = {}
        for stat in base:
            total = 0
            for item in self.inventory.equipped_items.values():
                if item:
                    # Check if the item has the stat attribute
                    total += getattr(item, f"{stat}_power", 0)
            equipped_bonuses[stat] = total
        # Calculate final stats
        for stat in base:
            # Set the final stat value
            setattr(self, f"_{stat}", base[stat] + class_bonuses[stat] + equipped_bonuses[stat])
        # Set the final stat value
        log.debug(f"{self.name} stats updated: {self.__dict__}")