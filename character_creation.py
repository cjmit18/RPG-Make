"""Character Creation Module
This module contains the Character class and its subclasses (NPC, Enemy, Player) for a game."""
import inventory_functions
import experience_functions
import class_creation
import items_list
import unit_test
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
        self.name: str = name
        self.attack: int = 10
        self.defense: int = 5
        self.speed: int = 10
        self.health: int = 100
        self.mana: int = 100
        self.stamina: int = 100
        self.lvls: experience_functions.Levels = experience_functions.Levels(self, level, experience)
        self.inventory: inventory_functions.Inventory = inventory_functions.Inventory(self)
        self.class_: class_creation.c_class = class_creation.c_class(self)
        self.update_stats()
    def __str__(self) -> str:
        return (f"{self.__class__.__name__}:\n"
                f"{self.lvls}\n"
                f"Class: {self.class_.class_}\n"
                f"{'-'*10}\n"
                f"Attack: {self.attack} ({self.bonus_attack()})\n"
                f"Defense: {self.defense} ({self.bonus_defense()})\n"
                f"Speed: {self.speed} ({self.bonus_speed()})\n"
                f"Health: {self.health} ({self.bonus_health()})\n"
                f"Mana: {self.mana} ({self.bonus_mana()})\n"
                f"Stamina: {self.stamina} ({self.bonus_stamina()})\n"
                f"{'-'*10}\n"
                f"{self.inventory}")
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}") + \
               (f"name={self.name}, lvl={self.lvl}, attack={self.attack}, defense={self.defense}, ") + \
               (f"speed={self.speed}, health={self.health}, mana={self.mana}, ") + \
               (f"stamina={self.stamina}, inventory={self.inventory}")    
    def __eq__(self, other) -> bool:
        if isinstance(other, Character):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def update_stats(self) -> None:
        """Update the character's stats based on the current level and class.
        This method is called whenever the character's level or class changes.
        """
        # Default stat calculation, override in subclasses if needed
        self.attack: int = 10 + (self.lvls.lvl - 1)
        self.defense: int = 5 + (self.lvls.lvl - 1)
        self.speed: int = 10 + (self.lvls.lvl - 1)
        self.health: int = 100 + (self.lvls.lvl - 1)
        self.mana: int = 100 + (self.lvls.lvl - 1)
        self.stamina: int = 100 + (self.lvls.lvl - 1)
    def change_class(self, class_):
        """Change the character's class and update stats accordingly."""
        self.class_: class_creation.c_class = class_(self)
    #-- Getters and Setters

    #----Name----
    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, name) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.") 
        self._name: str = name
   #- -Level----
    @property
    def lvl(self) -> int:
        return self._lvs.lvl
    @lvl.setter
    def lvl(self, lvl) -> None:
        self._lvls.lvl = lvl
        self.update_stats()
    #----Attack----
    def bonus_attack(self) -> int:
        """Calculate bonus attack based on equipped items."""
        total: int = 0
        weapon = self.inventory.equipped_items.get("weapon")
        if weapon is not None:
            total += weapon.attack_power
        shield = self.inventory.equipped_items.get("shield")
        if shield is not None:
            total += shield.attack_power
        if self.class_.attack is not 0:
            total += self.class_.attack
        return total
    @property
    def attack(self) -> int:
        return self._attack + self.bonus_attack()
    @attack.setter
    def attack(self, attack):
        if not isinstance(attack, int):
            raise TypeError("Attack must be an integer.")
        self._attack: int = max(0, attack)
    #----Defense----
    def bonus_defense(self) -> int:
        """Calculate bonus defense based on equipped items."""
        total = 0
        armor = self.inventory.equipped_items.get("armor")
        if armor is not None:
            total += armor.defense_power
        shield = self.inventory.equipped_items.get("shield")
        if shield is not None:
            total += shield.defense_power
        if self.class_.defense is not 0:
            total += self.class_.defense
        return total
    @property
    def defense(self) -> int:
        return self._defense + self.bonus_defense()
    @defense.setter
    def defense(self, defense) -> None:
        if not isinstance(defense, int):
            raise TypeError("Defense must be an integer.")
        self._defense: int = max(1, defense)
    #----Speed----
    def bonus_speed(self) -> int:
        """Calculate bonus speed based on equipped items."""
        total = 0
        boots = self.inventory.equipped_items.get("boots")
        if boots is not None:
            total += boots.speed_power
        if self.class_.speed is not 0:
            total += self.class_.speed
        return total
    @property
    def speed(self) -> int:
        return self._speed + self.bonus_speed()
    @speed.setter
    def speed(self, speed) -> None:
        if not isinstance(speed, int):
            raise TypeError("Speed must be an integer.")
        self._speed: int = max(1, speed)
    #----Health----
    def bonus_health(self) -> int:
        """Calculate bonus health based on equipped items."""
        total = 0
        ring = self.inventory.equipped_items.get("ring")
        if ring is not None:
            total += ring.health_power
        amulet = self.inventory.equipped_items.get("amulet")
        if amulet is not None:
            total += amulet.health_power
        if self.class_.health is not 0:
            total += self.class_.health
        return total
    @property
    def health(self) -> int:
        return self._health + self.bonus_health()
    @health.setter
    def health(self, health) -> None:
        if not isinstance(health, int):
            raise TypeError("Health must be an integer.")
        self._health: int = max(0, health)
    #----Mana----
    def bonus_mana(self) -> int:
        """Calculate bonus mana based on equipped items."""
        total = 0
        ring = self.inventory.equipped_items.get("ring")
        if ring is not None:
            total += ring.mana_power
        amulet = self.inventory.equipped_items.get("amulet")
        if amulet is not None:
            total += amulet.mana_power
        if self.class_.mana is not 0:
            total += self.class_.mana
        return total
    @property
    def mana(self) -> int:
        return self._mana + self.bonus_mana()
    @mana.setter
    def mana(self, mana) -> None:
        if not isinstance(mana, int):
            raise TypeError("Mana must be an integer.")
        self._mana: int = max(0, mana)
    
    #----Stamina----
    def bonus_stamina(self) -> int:
        """Calculate bonus stamina based on equipped items."""
        total = 0
        ring = self.inventory.equipped_items.get("ring")
        if ring is not None:
            total += ring.stamina_power
        amulet = self.inventory.equipped_items.get("amulet")
        if amulet is not None:
            total += amulet.stamina_power
        boots = self.inventory.equipped_items.get("boots")
        if boots is not None:
            total += boots.stamina_power
        if self.class_.stamina is not 0:
            total += self.class_.stamina
        return total
    @property
    def stamina(self) -> int:
        return self._stamina + self.bonus_stamina()
    @stamina.setter
    def stamina(self, stamina) -> None:
        if not isinstance(stamina, int):
            raise TypeError("Stamina must be an integer.")
        self._stamina: int = max(0, stamina)

    @property
    def inventory(self) -> inventory_functions.Inventory:
        return self._inventory
    @inventory.setter
    def inventory(self, inventory) -> None:
        if not isinstance(inventory, inventory_functions.Inventory):
            raise TypeError("Inventory must be an Inventory object.")
        self._inventory: inventory_functions.Inventory = inventory
    @property
    def class_(self) -> class_creation.c_class:
        return self._class_
    @class_.setter
    def class_(self, class_) -> None:
        if not isinstance(class_, class_creation.c_class):
            raise TypeError("Class must be a c_class object.")
        self._class_: class_creation.c_class = class_
        
class NPC(Character):
    def __init__(self, name: str = "NPC", level: int = 1) -> None:
        super().__init__(name, level)
    def __str__(self) -> str:
        return super().__str__()
    def __repr__(self)-> str:
        return super().__repr__()
    def __eq__(self, other)-> bool:
        if isinstance(other, NPC):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
class Enemy(Character):
    def __init__(self, name: str = "Enemy", level: int = 1) -> None:
        super().__init__(name, level)
        level: int = 1 if level == 0 else level
        if level == 1:
            potion: items_list.Potion = items_list.Health_Potion(lvl=1)
            self.inventory.add_item(potion, gen.generate_random_number(1, 3))
        elif level == 2:
            potion: items_list.Potion = items_list.Health_Potion(lvl=2)
            self.inventory.add_item(potion, gen.generate_random_number(1, 3))
        elif level == 3:
            potion: items_list.Potion = items_list.Health_Potion(lvl=3)
            self.inventory.add_item(potion, gen.generate_random_number(1, 3))
    def __str__(self) -> str:   
        return super().__str__()
    def __repr__(self) -> str:
        return super().__repr__()
    def __eq__(self, other) -> bool:
        if isinstance(other, Enemy):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def update_stats(self) -> None:
        """Update the enemy's stats based on the current level."""
        self.attack: int = self.lvls.lvl * 10
        self.defense: int = self.lvls.lvl * 5
        self.speed: int = self.lvls.lvl * 3
        self.health: int = (self.lvls.lvl * 2) * 10
        self.mana: int = round((self.lvls.lvl * 2) * 20)
        self.stamina: int = self.lvls.lvl * 5
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
    def __str__(self) -> str:
        return super().__str__()
    def __repr__(self) -> str:
        return super().__repr__()
    def __eq__(self, other):
        if isinstance(other, Player) or isinstance(other, Enemy):
            return self.name == other.name and self.lvl == other.lvl and self.attack == other.attack and self.defense == other.defense and self.speed == other.speed and self.health == other.health and self.mana == other.mana and self.stamina == other.stamina and self.experience == other.experience
        return False
    def update_stats(self) -> None:
        """Update the player's stats based on the current level."""
        self.attack: int = (self.lvls.lvl * 10)
        self.defense: int = (self.lvls.lvl * 3)
        self.speed: int = (self.lvls.lvl * 5 )
        self.health: int = ((self.lvls.lvl * 2) * 5)
        self.mana: int = (round((self.lvls.lvl * 2) * 10))
        self.stamina: int = (self.lvls.lvl * 10)