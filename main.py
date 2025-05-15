import character_creation
import inventory_functions
import combat_settings
import Item_functions
import os, random, time
import experience_functions
def main():
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Welcome to the RPG Game!")
    time.sleep(1)
    print("Creating your character...")
    time.sleep(1)
    
    # Create a character
    player = character_creation.Player("Hero", 10)
    player.attack = 50
    
    # Create an inventory for the character
    
    # Create some items
    sword = Item_functions.Weapon(name="Sword", description="A sharp sword.", price=10, attack_power=5)
    shield = Item_functions.Armor(name="Shield", description="A sturdy shield.", price=8, defense_power=3)
    potion = Item_functions.Consumable(name="Health Potion", description="Restores health.", effect="health", amount=10, duration=1)
    # Add items to the inventory
    player.inventory.add_item(sword, 1)
    player.inventory.add_item(shield, 1)
    player.inventory.add_item(potion, 2)
    # Display the inventory
    print("Your inventory:")
    player.inventory
    time.sleep(1)
    # Equip an item
    player.inventory.equip_item(sword, "weapon")
    player.inventory.equip_item(shield, "armor")
    player.inventory.equip_item(potion, "consumable")
    # Display equipped items
    print("Equipped items:")
    for slot, item in player.inventory.equipped_items.items():
        if item is not None:
            print(f"{slot.capitalize()}: {item.name}")
        else:
            print(f"{slot.capitalize()}: None")
    time.sleep(1)
    # Create an enemy
    enemy = character_creation.Enemy(name="Goblin",level = 5)
   
    # Start combat
    print(enemy)
if __name__ == "__main__":
    main()