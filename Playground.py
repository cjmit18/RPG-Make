import items_list as items
import character_creation
import inventory_functions
import class_creation
import combat_functions
import experience_functions
import os, random, time, logging
import gen
import weapon_list as weapons
import potion_list as potions
import armor_list as armors
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
axe = weapons.Axe(name="Knight's Axe", description="A sword for a knight", price=100, lvl=1, attack_power=20)
ring = items.Ring(name="Knight's Ring", description="A ring for a knight", price=100, lvl=1,)
amulet = items.Amulet(name="Knight's Amulet", description="An amulet for a knight", price=100, lvl=1)
character = character_creation.Player("TestChar")
character.change_class(class_creation.Knight)
print(character)
