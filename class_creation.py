import inventory_functions
import character_creation
import items_list
from weapon_list import Sword, Axe
from armor_list import Shield, Armor
from potion_list import Health_Potion
import gen
import uuid
import random
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
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
                if isinstance(item, (items_list.Item, items_list.Ring, items_list.Amulet)):
                    self.character.inventory.add_item(item)
                elif isinstance(item, (Sword, Axe)):
                    self.character.inventory.add_item(item)
                elif isinstance(item, (Shield, Armor)):
                    self.character.inventory.add_item(item)
                elif isinstance(item, Health_Potion):
                    self.character.inventory.add_item(item,gen.generate_random_number(1, 5))
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

class Knight(Base):
    def __init__(self, character: character_creation) -> None:
        stats = {
            "attack": 5,
            "defense": 5,
            "speed": 2,
            "health": 10,
            "mana": 5,
            "stamina": 5
        }
        """Knight class for the character """
        #Knight starts with a sword, shield, armor and boots
        starting_items: list = [
            Sword(name="Knight's Sword", description="A sword for a knight", price=100, lvl=1, attack_power=20),
            Armor(name="Knight's Shield", description="A shield for a knight", price=100, lvl=1, defense_power = 20),
            Armor(name="Knight's Armor", description="An armor for a knight", price=100, lvl=1, defense_power=20),
            items_list.Boots(name="Knight's Boots", description="Boots for a knight", price=100, lvl=1, speed_power=20),
            Health_Potion(name="Knight's Potion", description=f"A potion for a knight.\n Restores some health", price=100, lvl=1)
            ]
        #Knight starts with a sword, shield, armor and boots
        super().__init__(character, stats, starting_items, "Knight")
        
class Mage(Base):
    """Mage class for the character """
    def __init__(self, character: character_creation) -> None:
        starting_items: list = [
            #weapons.Staff(name="Mage's Staff", description="A staff for a mage", price=100, lvl=1, attack_power=20),
        ]
        stats = {
            "attack": 2,
            "defense": 2,
            "speed": 5,
            "health": 5,
            "mana": 10,
            "stamina": 5
        }
        super().__init__(character)
    
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Rogue(Base):
    """Rogue class for the character """
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        #Rogue starts with a dagger, leather armor and boots
        self.class_: str =  self.__class__.__name__
        self.attack: int = 5
        self.defense: int = 2
        self.speed: int = 5
        self.health: int = 5
        self.mana: int = 5
        self.stamina: int = 10
        log.info(f"{self.character.name} is now a {self.class_}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Healer(Base):
    """Healer class for the character """
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        #Healer starts with a staff, robe and boots
        self.class_: str = self.__class__.__name__
        self.attack: int = 2
        self.defense: int = 2
        self.speed: int = 2
        self.health: int = 5
        self.mana: int = 10
        self.stamina: int = 5
        log.info(f"{self.character.name} is now a {self.class_}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
