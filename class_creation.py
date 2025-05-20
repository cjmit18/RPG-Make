import inventory_functions
import character_creation
import items_list
from weapon_list import Sword, Axe, Dagger, Staff, Weapon, Off_Hand
from boots_list import Boot
from armor_list import Shield, Armor, Robe
from potion_list import Health_Potion, Mana_Potion, Potion
from amulet_list import Amulet
from ring_list import Ring
import gen
import uuid
import random
import logging
log = logging.getLogger(__name__)
class Base():
    """Base class for all classes
    This class is the base class for all classes in the game.
    It contains the character object and the class name.
    Attributes:
        character (character_creation): The character object.
        class_ (str): The name of the class.
        attack (int): The attack power of the class.
        defense (int): The defense power of the class.
        speed (int): The speed of the class.
        health (int): The health of the class.
        mana (int): The mana of the class.
        stamina (int): The stamina of the class.
    """
    def __init__(self, 
                character: character_creation, 
                stats: dict = {},
                starting_items: list = None,
                name: str = None) -> None:
        self.name: str = name
        self.character: character_creation = character
        self.class_: str = self.__class__.__name__
        for stat_name, stat_value in stats.items():
            """Set the stats of the class"""
            setattr(self.character, stat_name, stat_value)
            
        if starting_items: 
            """Add the starting items to the character's inventory"""
            for item in starting_items:
                if isinstance(item, (items_list.Item, Ring, Amulet)):
                    self.character.inventory.add_item(item)
                    self.character.inventory.equip_item(item)
                elif isinstance(item, (Weapon)):
                    self.character.inventory.add_item(item)
                    self.character.inventory.equip_item(item)
                elif isinstance(item, (Armor,Boot)):
                    self.character.inventory.add_item(item)
                    self.character.inventory.equip_item(item)
                elif isinstance(item,(Potion)):
                    self.character.inventory.add_item(item,gen.generate_random_number(1, 5))
        if self.__class__.__name__ is not "Base":
            log.info(f"{self.character.name} is now a {self.class_}!")
        
    def __str__(self) -> str:
        """String representation of the class"""
        parts = [f"Class Name: {self.class_}"]
        for stat in ["attack", "defense", "speed", "health", "mana", "stamina"]:
            parts.append(f"{stat.capitalize()}: {getattr(self, stat)}")
            bonus = getattr(self,stat,0)
            parts.append(f"{stat.capitalize()} Bonus: {bonus}")
        return "\n".join(parts)
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.character.name} ({self.character.lvl})>"
    @staticmethod
    def generate_random_class(cls, character: character_creation) -> None:
                """Generate a random class for the character"""
                if cls is None:
                    cls = random.choice([Knight, Mage, Rogue, Healer])
                else:
                    cls = cls
                return cls(character)
    @staticmethod
    def set_stats(self, stats: dict) -> None:
        """Set the stats of the class"""
        for stat_name, stat_value in stats.items():
            """Set the stats of the class"""
            setattr(self.character, stat_name, stat_value)
            log.info(f"{self.character.name}'s {stat_name} is now {stat_value}")
class Knight(Base):
    def __init__(self, character: character_creation) -> None:
        """Knight class for the character """
        lvl: int = character.lvls.lvl 
        self.character = character
        stats = {
            "attack": 5,
            "defense": 5,
            "speed": 2,
            "health": 10,
            "mana": 5,
            "stamina": 5
        }
        self.attack = stats["attack"] * lvl
        self.defense = stats["defense"] * lvl
        self.speed = stats["speed"] * lvl
        self.health = stats["health"] * lvl
        self.mana = stats["mana"] * lvl
        self.stamina = stats["stamina"] * lvl
        #Knight starts with a sword, shield, armor and boots
        starting_items: list = [
            Sword(name="Knight's Sword", description="A sword for a knight", price=100, lvl=1, attack_power=20),
            Shield(name="Knight's Shield", description="A shield for a knight", price=100, lvl=1, defense_power = 20),
            Armor(name="Knight's Armor", description="An armor for a knight", price=100, lvl=1, defense_power=20),
            Boot(name="Knight's Boots", description="Boots for a knight", price=100, lvl=1, speed_power=20),
            Health_Potion(name="Knight's Potion", description=f"A potion for a knight.\n Restores some health", price=100, lvl=1),
            Mana_Potion(name="Knight's Mana Potion", description=f"A potion for a knight.\n Restores some mana", price=100, lvl=1)
            ]
        super().__init__(character, stats, starting_items, "Knight")
        
class Mage(Base):
    """Mage class for the character """
    def __init__(self, character: character_creation) -> None:
        starting_items: list = [
            Staff(name="Mage's Staff", description="A staff for a mage", price=100, lvl=1, attack_power=20),
            Robe(name="Mage's Robe", description="A robe for a mage", price=100, lvl=1, defense_power=20),
            Boot(name="Mage's Boots", description="Boots for a mage", price=100, lvl=1, speed_power=20),
            Health_Potion(name="Mage's Potion", description=f"A potion for a mage.\n Restores some health", price=100, lvl=1),
            Mana_Potion(name="Mage's Mana Potion", description=f"A potion for a mage.\n Restores some mana", price=100, lvl=1)
            ]
        if gen.generate_random_number(1, 100) < 10:
            starting_items.append(Amulet(name="Mage's Amulet", description="An amulet for a mage", price=100, lvl=1, mana_power=20))
        stats = {
            "attack": 2,
            "defense": 2,
            "speed": 5,
            "health": 5,
            "mana": 10,
            "stamina": 5
        }
        self.attack: int = stats["attack"]
        self.defense: int = stats["defense"]
        self.speed: int = stats["speed"]
        self.health: int = stats["health"]
        self.mana: int = stats["mana"]
        self.stamina: int = stats["stamina"]
        super().__init__(character, stats, starting_items, "Mage")
class Rogue(Base):
    """Rogue class for the character """
    def __init__(self, character: character_creation) -> None:
        #Rogue starts with a dagger, leather armor and boots
        starting_items: list = [
            Dagger(name="Rogue's Dagger", description="A dagger for a rogue", price=100, lvl=1, attack_power=20),
            Off_Hand(name="Rogue's Dagger", description="A dagger for a rogue", price=100, lvl=1, attack_power=20),
            Armor(name="Rogue's Armor", description="An armor for a rogue", price=100, lvl=1, defense_power=20),
            Boot(name="Rogue's Boots", description="Boots for a rogue", price=100, lvl=1, speed_power=20),
            Health_Potion(name="Rogue's Potion", description=f"A potion for a rogue.\n Restores some health", price=100, lvl=1)
        ]
        if gen.generate_random_number(1, 100) < 10:
            starting_items.append(Amulet(name="Rogue's Amulet", description="An amulet for a rogue", price=100, lvl=1, stamina_power=20))
        stats = {
            "attack": 5,
            "defense": 2,
            "speed": 5,
            "health": 5,
            "mana": 5,
            "stamina": 5
        }
        self.attack: int = stats["attack"]
        self.defense: int = stats["defense"]
        self.speed: int = stats["speed"]
        self.health: int = stats["health"]
        self.mana: int = stats["mana"]
        self.stamina: int = stats["stamina"]
        super().__init__(character, stats, starting_items, "Rogue")
class Healer(Base):
    """Healer class for the character """
    def __init__(self, character: character_creation) -> None:
        #Healer starts with a staff, robe and boots
        starting_items: list = [
            Staff(name="Healer's Staff", description="A staff for a healer", price=100, lvl=1, attack_power=20),
            Robe(name="Healer's Robe", description="A robe for a healer", price=100, lvl=1, defense_power=20),
            Boot(name="Healer's Boots", description="Boots for a healer", price=100, lvl=1, speed_power=20),
            Health_Potion(name="Healer's Potion", description=f"A potion for a healer.\n Restores some health", price=100, lvl=1),
            Mana_Potion(name="Healer's Mana Potion", description=f"A potion for a healer.\n Restores some mana", price=100, lvl=1)
        ]
        if gen.generate_random_number(1, 100) < 10:
            starting_items.append(Amulet(name="Healer's Amulet", description="An amulet for a healer", price=100, lvl=1, health_power=20, mana_power=20))
        #Healer has a chance to start with an amulet
            if gen.generate_random_number(1, 100) < 10:
                starting_items.append(Ring(name="Healer's Ring", description="A ring for a healer", price=100, lvl=1, health_power=200, mana_power=20))
        #Healer has a chance to start with a ring percent is 1%
        stats = {
            "attack": 2,
            "defense": 2,
            "speed": 2,
            "health": 5,
            "mana": 10,
            "stamina": 5
        }
        self.attack: int = stats["attack"]
        self.defense: int = stats["defense"]
        self.speed: int = stats["speed"]
        self.health: int = stats["health"]
        self.mana: int = stats["mana"]
        self.stamina: int = stats["stamina"]
        super().__init__(character, stats, starting_items, "Healer")