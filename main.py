import character_creation
import inventory_functions
import combat_settings
import Item_functions
import os
import experience_functions
player = character_creation.Player()
weapon = Item_functions.Weapon("Sword", "A sharp blade.", 10, 1, 15)
armor = Item_functions.Armor("Shield", "A sturdy shield.", 20, 1, 10)
consumable = Item_functions.Consumable("Health Potion", "Restores health.", 5, 3, "Restores 20 health.")
player.inventory.add_item(weapon, weapon.quantity)
player.inventory.equip_item(weapon, "weapon")

