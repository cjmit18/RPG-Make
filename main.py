import character_creation
import inventory_functions
import combat_settings
import os
import experience_functions
def main():
    # Create a player player
    player = character_creation.Player("Hero")
    player.speed = 31
    player.attack = 30
    player.inventory.add_item("Potion", 5)
    player.inventory.add_item("Sword", 1)
    player.inventory.add_item("Shield", 1)
    # Create an enemy player
    enemy = character_creation.Enemy("Monster", 50)
    enemy.attack = 30
    enemy.speed = 5
    enemy.health = 50
    # Add items to inventories
    return player, enemy
if __name__ == "__main__":
    player, enemy = main()
combat = combat_settings.Combat(player, enemy)
combat.turns(player, enemy)
print(enemy.lvl)
print(player.lvl)
    
   