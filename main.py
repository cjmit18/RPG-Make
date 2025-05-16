import character_creation
import inventory_functions
import combat_settings
import Item_functions
import os, random, time
import experience_functions
def generate_random_number(min_value=1, max_value=10):
    return random.randint(min_value, max_value)
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
def main():
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Welcome to the RPG Game!")
    #time.sleep(1)
    print("Creating your character...")
    #time.sleep(1)
    
    # Create a character
    player = character_creation.Player("Hero", 1)
    character = character_creation.Character("Wizard", 50)
    character.attack = character.lvl.lvl * 2
    character.defense = character.lvl.lvl * 2
    character.health = 100
   
    # Create an inventory for the character
    
    # Create some items
    sword = Item_functions.Weapon(name="Sword", description="A sharp sword.", price=10, attack_power=5)
    shield = Item_functions.Armor(name="Shield", description="A sturdy shield.", price=8, defense_power=3)
    potion = Item_functions.Consumable(name="Health Potion", description="Restores health.", effect="health", amount=10, duration=1)
    # Add items to the inventory
    random_item = Item_functions.Items.generate(lvl  = generate_random_number(1,3))
    character.inventory.add_item(sword, 1)
    character.inventory.add_item(shield, 1)
    character.inventory.add_item(potion, 2)
    character.inventory.add_item(random_item, 1)
    # Display the inventory
    print("Your inventory:")
    #time.sleep(1)
    # Equip an item
    character.inventory.equip_item(sword, "weapon")
    character.inventory.equip_item(shield, "armor")
    character.inventory.equip_item(potion, "consumable")
    #Display equipped items
    print("Equipped items:")
    for slot, item in character.inventory.equipped_items.items():
        if item is not None:
            print(f"{slot.capitalize()}: {item.name}")
        else:
            print(f"{slot.capitalize()}: None")
    #time.sleep(1)
    # Create an enemy
    enemy = character_creation.Enemy(name="Dragon",level = 50)
    #start combat
    #print(f"A wild {enemy.name} appears!")
    #time.sleep(1)
    # Simulate combat
    print(character.inventory.items[random_item.id][0].price)
if __name__ == "__main__":
    main()