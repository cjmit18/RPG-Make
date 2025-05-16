import character_creation
import inventory_functions
import combat_settings
import Item_functions
import os, random, time
import experience_functions
def generate_random_number(min_value=1, max_value=10):
    return random.randint(min_value, max_value)
def generate_random_float(min_value=1.0, max_value=10.0):
    return random.uniform(min_value, max_value)
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
    character = character_creation.Character("Wizard", 10)
    character.speed = 1000
   
    # Create an inventory for the character
    
    # Create some items
    sword = Item_functions.Weapon(name="Sword", description="A sharp sword.", price=10, attack_power=5, lvl=2)
    shield = Item_functions.Armor(name="Shield", description="A sturdy shield.", price=8, defense_power=650)
    potion = Item_functions.Consumable(name="Health Potion", description="Restores health.", effect="health", amount=10, duration=1)
    # Add items to the inventory 
    random_item = Item_functions.Items.generate(lvl = generate_random_number(1,3),item_type = "weapon",effect = "", attack_power=1500, quantity=2)# duration = generate_random_number(1, 5))
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
    character.inventory.use_item(potion)
    print(character.inventory.items[random_item.id]["item"])
    # Display the result
if __name__ == "__main__":
    main()