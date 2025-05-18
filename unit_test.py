import character_creation
import inventory_functions
import combat_functions
import items_list as items
import experience_functions
import os, random, time,logging
import class_creation
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
def generate_random_number(min_value=1, max_value=10):
    return random.randint(min_value, max_value)
def generate_random_float(min_value=1.0, max_value=10.0):
    return random.uniform(min_value, max_value)
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
def main():
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')
    # Create a character
    character = character_creation.Character(name="Hero", level=1)
    # Create an enemy
    enemy = character_creation.Enemy(name="Goblin", level=1)
    # Create a combat instance
    combat = combat_functions.Combat(character, enemy)
    # Start combat
    combat.turns(character, enemy)
    print(character)
    print(character.inventory)

if __name__ == "__main__":
    main()
    # Test inventory
    