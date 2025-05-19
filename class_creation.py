import inventory_functions
import character_creation
import experience_functions
import combat_functions
import items_list
import uuid, random, time
import logging, os
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
class c_class():
    def __init__(self, character: character_creation) -> None:
        self.character: character_creation = character
        self.class_: str = ""
        self.attack: int = 0
        self.defense: int = 0
        self.speed: int = 0
        self.health: int = 0
        self.mana: int = 0
        self.stamina: int = 0
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Knight(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        sword = items_list.Sword(name="Knight's Sword", description="A sword for a knight", price=100, lvl=1, attack_power=20)
        shield = items_list.Shield(name="Knight's Shield", description="A shield for a knight", price=100, lvl=1, defense_power=20)
        armor = items_list.Armor(name="Knight's Armor", description="An armor for a knight", price=100, lvl=1, defense_power=20)
        boots = items_list.Boots(name="Knight's Boots", description="Boots for a knight", price=100, lvl=1, speed_power=20)
        self.character.inventory.add_item(boots)
        self.character.inventory.add_item(armor)
        self.character.inventory.add_item(shield)
        self.character.inventory.add_item(sword)
        self.class_: str = self.__class__.__name__
        self.attack: int = 5
        self.defense: int = 5
        self.speed: int = 2
        self.health: int = 10
        self.mana: int = 5
        self.stamina: int = 5
        log.info(f"{self.character.name} is now a {self.class_}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Mage(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        self.class_: str = self.__class__.__name__
        self.attack: int = 2
        self.defense: int = 2
        self.speed: int = 5
        self.health: int = 5
        self.mana: int = 10
        self.stamina: int = 5
        log.info(f"{self.character.name} is now a {self.class_}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Rogue(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
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
class Healer(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
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
    def generate_random_class(cls, character: character_creation) -> c_class:
        class_ = random.choice([Knight, Mage, Rogue])
        return class_(character)
    