import inventory_functions
import Item_functions
import character_creation
import experience_functions
import combat_functions
import uuid, random, time
import logging, os
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
class c_class():
    def __init__(self, character: character_creation) -> None:
        self.character = character
        self.class_ = None
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Knight(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        self.class_ = "Knight"
        character.attack += 5
        character.defense += 5
        character.speed += 2
        character.health += 10
        character.mana += 5
        character.stamina += 5
        log.info(f"{self.character.name} is now a {self.class_}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Mage(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        self.class_ = "Mage"
        self.character.attack += 2
        self.character.defense += 2
        self.character.speed += 5
        self.character.health += 5
        self.character.mana += 10
        self.character.stamina += 5
        self.character.inventory_functions.Inventory(self)
        log.info(f"{self.character.name} is now a {self.c_class}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Rogue(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        self.class_ = "Rogue"
        self.character.attack += 5
        self.character.defense += 2
        self.character.speed += 5
        self.character.health += 5
        self.character.mana += 5
        self.character.stamina += 10
        log.info(f"{self.character.name} is now a {self.c_class}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
class Healer(c_class):
    def __init__(self, character: character_creation) -> None:
        super().__init__(character)
        self.class_ = "Healer"
        self.character.attack += 2
        self.character.defense += 2
        self.character.speed += 2
        self.character.health += 5
        self.character.mana += 10
        self.character.stamina += 5
        log.info(f"{self.character.name} is now a {self.c_class}!")
    def __str__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    def __repr__(self) -> str:
        return f"Name: {self.character.name}\nLevel: {self.character.lvl} Experience: {self.character.lvl.experience}\nHealth: {self.character.health}\nMana: {self.character.mana}\nStamina: {self.character.stamina}\nAttack: {self.character.attack}\nDefense: {self.character.defense}\nSpeed: {self.character.speed}"
    @classmethod
    def change_class(cls, character: character_creation) -> c_class:
        if character.class_ == "Knight":
            return Knight(character)
        elif character.class_ == "Mage":
            return Mage(character)
        elif character.class_ == "Rogue":
            return Rogue(character)
        else:
            raise ValueError("Invalid class type.")
    @classmethod
    def generate_random_class(cls, character: character_creation) -> c_class:
        class_ = random.choice([Knight, Mage, Rogue])
        return class_(character)
    