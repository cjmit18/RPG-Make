import items_list as items
import character_creation
import inventory_functions
import class_creation
import combat_functions
import experience_functions
import os, random, time, logging
import gen
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

character = character_creation.Character("TestChar", 2, 100)
character.change_class(class_creation.Knight)
print(character)
