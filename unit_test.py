import character_creation
import inventory_functions
import combat_functions
import items_list as items
import experience_functions
import os, random, time,logging
import class_creation
import gen
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

import unittest
def main():
    """Main function to run the combat test."""
    # Create a character and an enemy
    character = character_creation.Character(name="Hero")
    enemy = character_creation.Enemy(name="Goblin")

    # Initialize combat
    character.inventory.add_item(items.Ring(lvl=1))
    character.inventory.equip_by_name("Ring")
    print(character)
if __name__ == "__main__":
    main()
