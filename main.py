import character_creation
import inventory_functions
import combat_settings
import Item_functions
import os
import experience_functions
def main():
    weapon_generation = []
    for i in range(5):
        weapon = Item_functions.Weapon()
        weapon_generation.append(weapon)
    weapon_generation[0].attack_power = 100
    weapon_generation[0].name = "Sword of Destiny"
    return weapon_generation
if __name__ == "__main__":
    weapons = main()
print(weapons[0])