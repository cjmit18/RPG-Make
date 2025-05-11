import character_creation
import inventory_functions
import combat_settings
def main():
    # Create a player player
    player = character_creation.Player("Hero")
    player.speed = 10
    player.attack = 15
    player.inventory.add_item("Potion", 5)
    player.inventory.add_item("Sword", 1)
    player.inventory.add_item("Shield", 1)
    # Create an enemy player
    enemy = character_creation.Enemy("Monster")
    enemy.speed = 5
    enemy.health = 10
    # Add items to inventories
    return player, enemy
if __name__ == "__main__":
    player, enemy = main()
    # Create a combat instance
    combat = combat_settings.Combat(player, enemy)
    # Start the combat test
    combat.turns(player, enemy)
    # Test the combat settings
