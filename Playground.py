
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
import amulet_list as amulets
from ring_list import Ring
from boots_list import Boot
import logging
logging.basicConfig(level=logging.INFO)
ring = Ring(name="Ring of Power", description="A powerful ring", price=100, effect="health", lvl=1, health_power=10, mana_power=5, stamina_power=3)
character = character_creation.Player("TestChar")
amulet = amulets.Amulet(name="Amulet of Power", description="A powerful amulet", price=100, effect="health", lvl=1, health_power=10, mana_power=5, stamina_power=3)
character.change_class(class_creation.Rogue)
print(character)