
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
character = character_creation.Player("TestChar")
character.change_class(class_creation.Knight)
print(character)