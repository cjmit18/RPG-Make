"""Character Creation Module
This module contains the Character class and its subclasses (NPC, Enemy, Player) for a game."""
import inventory_functions
import experience_functions
import class_creation
import items_list
import potion_list as potions
import gen
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
                f"Attack: {self.attack} ({self.bonus_attack()})\n" #Base stats + bonus stats
                f"Defense: {self.defense} ({self.bonus_defense()})\n" 
                f"Speed: {self.speed} ({self.bonus_speed()})\n"
                f"Health: {self.health} ({self.bonus_health()})\n"
                f"Mana: {self.mana} ({self.bonus_mana()})\n"
                f"Stamina: {self.stamina} ({self.bonus_stamina()})\n"
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
        lvl_offset = self.lvls.lvl - 1
        self._attack: int = 10 + lvl_offset 
        self._defense: int = 5 + lvl_offset
        self._speed: int = 10 + lvl_offset
        self._health: int = 100 + lvl_offset
        self._mana: int = 100 + lvl_offset
        self._stamina: int = 100 + lvl_offset
    def change_class(self, class_):
        """Change the character's class and update stats accordingly."""
        self.class_: class_creation.Base = class_(self) 
        self.update_stats()
    def bonus_health(self) -> int:
        """Calculate bonus health based on equipped items."""
        total = 0
        # Check for equipped items in the inventory
        for slot in ["amulet", "ring"]:
            item = self.inventory.equipped_items.get(slot)
            # If the item is not None, add its health power to the total
            if item:
                # Check if the item has a health_power attribute
                total += getattr(item, "health_power", 0)
        # Add class health bonus if applicable
        total += getattr(self.class_, "health", 0)  
        # Check if the class has a health attribute
        return total
    def bonus_mana(self) -> int:
        """Calculate bonus mana based on equipped items."""
        total = 0
        for slot in ["amulet", "ring"]:
            item = self.inventory.equipped_items.get(slot)
            # If the item is not None, add its mana power to the total
            if item:
                # Check if the item has a mana_power attribute
                total += getattr(item, "mana_power", 0)
        # Add class mana bonus if applicable
        total += getattr(self.class_, "mana", 0)
        # Check if the class has a mana attribute
        return total
                
    def bonus_attack(self) -> int:
        """Calculate bonus attack based on equipped items."""
        total: int = 0
        # Check for equipped items in the inventory
        for slot in ["weapon", "shield", "armor"]:
            item = self.inventory.equipped_items.get(slot)
            # If the item is not None, add its attack power to the total
            if item :
                # Check if the item has an attack_power attribute
                total += getattr(item, "attack_power", 0)
        # Add class attack bonus if applicable
        total += getattr(self.class_, "attack", 0)
        # Check if the class has an attack attribute
        return total
    def bonus_defense(self) -> int:
        """Calculate bonus defense based on equipped items."""
        total = 0
        # Check for equipped items in the inventory
        for slot in ["shield", "armor"]:
            item = self.inventory.equipped_items.get(slot)
            # If the item is not None, add its defense power to the total
            if item:
                # Check if the item has a defense_power attribute
                total += getattr(item, "defense_power", 0)
        # Add class defense bonus if applicable
        total += getattr(self.class_, "defense", 0)
        # Check if the class has a defense attribute
        return total
    def bonus_speed(self) -> int:
        """Calculate bonus speed based on equipped items."""
        total = 0
        # Check for equipped items in the inventory
        for slot in ["boots"]:
            item = self.inventory.equipped_items.get(slot)
            # If the item is not None, add its speed power to the total
            if item:
                # Check if the item has a speed_power attribute
                total += getattr(item, "speed_power", 0)
        # Add class speed bonus if applicable
        total += getattr(self.class_, "speed", 0)
        # Check if the class has a speed
        return total
    def bonus_stamina(self) -> int:
        """Calculate bonus stamina based on equipped items."""
        total = 0
        # Check for equipped items in the inventory
        for slot in ["boots"]:
            item = self.inventory.equipped_items.get(slot)
            # If the item is not None, add its stamina power to the total
            if item:
                # Check if the item has a stamina_power attribute
                total += getattr(item, "stamina_power", 0)
        # Add class stamina bonus if applicable
        total += getattr(self.class_, "stamina", 0)
        return total
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
        return self._lvls.lvl
    @lvl.setter
    def lvl(self, lvl) -> None:
        self._lvls.lvl = lvl
        self.update_stats() #Update stats when level changes
    #----Properties for public access----
    #----Attack----
    #Attack is a property that handles the attack of the character
    #It is a property to keep the code clean and organized
    @property
    def attack(self) -> int:
        return self._attack + self.bonus_attack()
    @attack.setter
    def attack(self, attack):
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        self._attack: int = max(0, attack)
    #----Defense----
    #Defense is a property that handles the defense of the character
    #It is a property to keep the code clean and organized
    @property
    def defense(self) -> int:
        return self._defense + self.bonus_defense()
    @defense.setter
    def defense(self, defense) -> None:
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        self._defense: int = max(0, defense)
    #----Speed----
    #Speed is a property that handles the speed of the character
    #It is a property to keep the code clean and organized
    @property
    def speed(self) -> int:
        return self._speed + self.bonus_speed()
    @speed.setter
    def speed(self, speed) -> None:
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        self._speed: int = max(0, speed)
    #----Health----
    #Health is a property that handles the health of the character
    #It is a property to keep the code clean and organized
    @property
    def health(self) -> int:
        return self._health + self.bonus_health()
    @health.setter
    def health(self, health) -> None:
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        self._health: int = max(0, health)
    #----Mana----
    #Mana is a property that handles the mana of the character
    #It is a property to keep the code clean and organized
    @property
    def mana(self) -> int:
        return self._mana + self.bonus_mana()
    @mana.setter
    def mana(self, mana) -> None:
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        self._mana: int = max(0, mana)
    
    #----Stamina----
    #Stamina is a property that handles the stamina of the character
    #It is a property to keep the code clean and organized
    @property
    def stamina(self) -> int:
        return self._stamina + self.bonus_stamina()
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
        """Update the enemy's stats based on the current level."""
        # Update enemy stats based on level
        
        lvl = self.lvls.lvl
        self._attack: int = lvl * 10
        self._defense: int = lvl * 5
        self._speed: int = lvl * 3
        self._health: int = lvl * 2 * 10
        self._mana: int = round(lvl * 2 * 20)
        self._stamina: int = lvl * 5
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
    def update_stats(self) -> None:
        """Update the player's stats based on the current level."""
        # Update player stats based on level
        lvl = self.lvls.lvl
        # Base stats for the player
        self._attack: int = lvl * 10
        self._defense: int = lvl * 3
        self._speed: int = lvl * 5 
        self._health: int = lvl* 2 * 5
        self._mana: int = round(lvl * 2 * 10)
        self._stamina: int = lvl * 10