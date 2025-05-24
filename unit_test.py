"""Unit tests for the RPG game modules."""
# This module contains unit tests for character creation, item lists, class creation, experience functions, inventory functions, and combat functions.
import character_creation
import inventory_functions
import combat_functions
import items_list as items
import weapon_list as weapons
import potion_list as potions
import armor_list as armors
import amulet_list as amulets
import experience_functions
import ring_list as rings
import class_creation
import boots_list as boots
import save_load
import gen
import json
import os
import unittest
class TestCharacterCreation(unittest.TestCase):
    def test_character_init(self):
        char = character_creation.Character("TestChar", 2, 100)
        self.assertEqual(char.name, "TestChar")
        self.assertEqual(char.lvls.lvl, 2)
        self.assertEqual(char.lvls.experience, 100)

    def test_player_inheritance(self):
        player = character_creation.Player("Hero", 3)
        self.assertIsInstance(player, character_creation.Character)
        self.assertEqual(player.name, "Hero")
        self.assertEqual(player.lvls.lvl, 3)
    def test_player_init(self):
        player = character_creation.Player("Hero", 3, 200)
        self.assertEqual(player.name, "Hero")
        self.assertEqual(player.lvls.lvl, 3)
        self.assertEqual(player.lvls.experience, 200)
    def test_player_experience(self):
        player = character_creation.Player("Hero", 3, 200)
        self.assertEqual(player.lvls.experience, 200)
        player.lvls.add_experience(100)
        self.assertEqual(player.lvls.experience, 300)
        player.lvls.remove_experience(50)
        self.assertEqual(player.lvls.experience, 250)
    def test_player_level_up(self):
        player = character_creation.Player("Hero", 1, 100)
        self.assertEqual(player.lvls.lvl, 1)
        player.lvls.add_experience(100)
        self.assertEqual(player.lvls.lvl, 2)
        self.assertEqual(player.lvls.experience, 0)
    def test_enemy_inheritance(self):
        enemy = character_creation.Enemy("Goblin", 1)
        self.assertIsInstance(enemy, character_creation.Character)
        self.assertEqual(enemy.name, "Goblin")
        self.assertEqual(enemy.lvls.lvl, 1)
        self.assertEqual(enemy.lvls.experience, 100)
    def test_enemy_init(self):
        enemy = character_creation.Enemy("Goblin", 1, 50)
        self.assertEqual(enemy.name, "Goblin")
        self.assertEqual(enemy.lvls.lvl, 1)
        self.assertEqual(enemy.lvls.experience, 50)
    def test_enemy_experience(self):
        enemy = character_creation.Enemy("Goblin", 1, 50)
        self.assertEqual(enemy.lvls.experience, 50)
        enemy.lvls.add_experience(100)
        self.assertEqual(enemy.lvls.experience, 150)
        enemy.lvls.remove_experience(50)
        self.assertEqual(enemy.lvls.experience, 100)
    
class TestItemsList(unittest.TestCase):
    def test_item_init(self):
        item = weapons.Sword(name="Sword", description="Sharp blade", price=100, lvl=2)
        self.assertEqual(item.name, "Sword")
        self.assertEqual(item.description, "Sharp blade")
        self.assertEqual(item.price, 100)
        self.assertEqual(item.lvl, 2)

    def test_potion_init(self):
        potion = potions.Health_Potion(name="Health Potion", description="Restores health", price=50, amount=20)
        self.assertEqual(potion.name, "Health Potion")
        self.assertEqual(potion.description, "Restores health")
        self.assertEqual(potion.price, 50)
        self.assertEqual(potion.amount, 20)
    def test_amulet_init(self):
        amulet = armors.Amulet(name="Amulet", description="Protective amulet", price=200, effect="defense", amount=10)
        self.assertEqual(amulet.name, "Amulet")
        self.assertEqual(amulet.description, "Protective amulet")
        self.assertEqual(amulet.price, 200)
        self.assertEqual(amulet.effect, "defense")
        self.assertEqual(amulet.amount, 10)
    def test_armor_init(self):
        armor = armors.Armor(name="Armor", description="Protective armor", price=300, defense_power=50)
        self.assertEqual(armor.name, "Armor")
        self.assertEqual(armor.description, "Protective armor")
        self.assertEqual(armor.price, 300)
        self.assertEqual(armor.defense_power, 50)
    def test_shield_init(self):
        shield = armors.Shield(name="Shield", description="Protective shield", price=150, defense_power=30, lvl=1, attack_power=10)
        self.assertEqual(shield.lvl, 1)
        self.assertEqual(shield.name, "Shield")
        self.assertEqual(shield.description, "Protective shield")
        self.assertEqual(shield.price, 150)
        self.assertEqual(shield.defense_power, 30)
        self.assertEqual(shield.attack_power, 10)
    def test_robe_init(self):
        robe = armors.Robe(name="Robe", description="Protective robe", price=100, defense_power=20, lvl=1)
        self.assertEqual(robe.lvl, 1)
        self.assertEqual(robe.name, "Robe")
        self.assertEqual(robe.description, "Protective robe")
        self.assertEqual(robe.price, 100)
        self.assertEqual(robe.defense_power, 20)
    def test_amulet_list_init(self):
        amulet = amulets.Amulet(name="Amulet", description="Protective amulet", price=200, effect="defense", amount=10)
        self.assertEqual(amulet.name, "Amulet")
        self.assertEqual(amulet.description, "Protective amulet")
        self.assertEqual(amulet.price, 200)
        self.assertEqual(amulet.effect, "defense")
        self.assertEqual(amulet.amount, 10)
    def test_ring_init(self):
        ring = rings.Ring(name="Ring", description="Magical ring", price=250, effect="magic", health_power=5, mana_power=10, stamina_power=3)
        self.assertEqual(ring.name, "Ring")
        self.assertEqual(ring.description, "Magical ring")
        self.assertEqual(ring.price, 250)
        self.assertEqual(ring.effect, "magic")
        self.assertEqual(ring.health_power, 5)
        self.assertEqual(ring.mana_power, 10)
        self.assertEqual(ring.stamina_power, 3)
    def test_weapon_init(self):
        weapon = weapons.Sword(name="Sword", description="Sharp blade", price=100, lvl=2, attack_power=30)
        self.assertEqual(weapon.name, "Sword")
        self.assertEqual(weapon.description, "Sharp blade")
        self.assertEqual(weapon.price, 100)
        self.assertEqual(weapon.lvl, 2)
        self.assertEqual(weapon.attack_power, 30)
    def test_boots_init(self):
        boots = armors.Boots(name="Boots", description="Sturdy boots", price=80, defense_power=15, lvl=1)
        self.assertEqual(boots.name, "Boots")
        self.assertEqual(boots.description, "Sturdy boots")
        self.assertEqual(boots.price, 80)
        self.assertEqual(boots.defense_power, 15)
        self.assertEqual(boots.lvl, 1)
class TestClassCreation(unittest.TestCase):
    def test_knight_class(self):
        char = character_creation.Character("KnightGuy")
        knight = class_creation.Knight(char)
        self.assertEqual(knight.job, "Knight")
        self.assertEqual(knight.character._base_stats.attack, 5)
    def test_mage_class(self):
        char = character_creation.Character("MageGuy")
        mage = class_creation.Mage(char)
        self.assertEqual(mage.job, "Mage")
        self.assertEqual(mage.character._base_stats.mana, 10)
    def test_rogue_class(self):
        char = character_creation.Character("RogueGuy")
        rogue = class_creation.Rogue(char)
        self.assertEqual(rogue.job, "Rogue")
        self.assertEqual(rogue.character._base_stats.attack, 5)
    def test_healer_class(self):
        char = character_creation.Character("HealerGuy")
        healer = class_creation.Healer(char)
        self.assertEqual(healer.job, "Healer")
        self.assertEqual(healer.character._base_stats.mana, 10)

class TestExperienceFunctions(unittest.TestCase):
    def test_levels(self):
        char = character_creation.Character("LevelGuy", 5, 200)
        self.assertEqual(char.lvls.lvl, 5)
        self.assertEqual(char.lvls.experience, 200)
    def test_experience_gain(self):
        char = character_creation.Enemy("ExpGuy", 0, 0) # Enemy starts at level 0 because level 1 gives 100 exp still works as a test
        char.lvls.add_experience(50)
        self.assertEqual(char.lvls.experience, 50)
        char.lvls.add_experience(100)
        self.assertEqual(char.lvls.experience, 150)
        char.lvls.add_experience(200)
        self.assertEqual(char.lvls.experience, 350)

class TestInventoryFunctions(unittest.TestCase):
    def test_inventory_add(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        item = items.Item(name="Potion")
        inv.add_item(item)
        self.assertIn(item.id, inv.items)
    def test_inventory_remove(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        item = items.Item(name="Potion")
        inv.add_item(item)
        self.assertIn(item.id, inv.items)
        inv.remove_item(item)
        self.assertNotIn(item.id, inv.items)
    def test_inventory_use_item(self):
        char = character_creation.Character("InvGuy")
        potion = potions.Health_Potion(name="Health Potion", description="Restores health", price=50, amount=20)
        char.inventory.add_item(potion)
        self.assertIn(potion.id, char.inventory.items)
        char.inventory.use_item(potion)
        self.assertNotIn(potion.id, char.inventory.items)
    def test_inventory_use_item_not_found(self):
        char = character_creation.Character("InvGuy")
        potion = potions.Health_Potion(name="Health Potion", description="Restores health", price=50, amount=20)
        char.inventory.add_item(potion)
        char.inventory.remove_item(potion)
        with self.assertRaises(ValueError):
            char.inventory.use_item(potion)
    def test_inventory_list_items(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        item1 = items.Item(name="Potion")
        item2 = items.Item(name="Elixir")
        inv.add_item(item1)
        inv.add_item(item2)
        self.assertIn(item1.id, inv.items)
        self.assertIn(item2.id, inv.items)
    def test_inventory_list_empty(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        if inv.items:
            self.fail("Inventory should be empty but it is not.")
        else:
            self.assertEqual(len(inv.items), 0)
    def test_inventory_list_not_empty(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        item = items.Item(name="Potion")
        inv.add_item(item)
        if not inv.items:
            self.fail("Inventory should not be empty but it is.")
        else:
            self.assertNotEqual(len(inv.items), 0)
    def test_inventory_list_item_count(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        item = items.Item(name="Potion")
        item2 = items.Item(name="Elixir")
        inv.add_item(item)
        self.assertEqual(len(inv.items), 1)
        inv.add_item(item2)
        self.assertEqual(len(inv.items), 2)
    def test_inventory_list_item_count_empty(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        if inv.items:
            self.fail("Inventory should be empty but it is not.")
        else:
            self.assertEqual(len(inv.items), 0)
        
class TestCombatFunctions(unittest.TestCase):
    pass
class TestItemsList(unittest.TestCase):
    def test_item_init(self):
        item = items.Item(name="Test Item", description="A test item", price=100, lvl=1)
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.description, "A test item")
        self.assertEqual(item.price, 100)
        self.assertEqual(item.lvls.lvl, 1)
    def test_consumable_init(self):
        consumable = items.Consumable(name="Test Consumable", description="A test consumable", price=50, effect="heal", amount=20, duration=5, lvl=1)
        self.assertEqual(consumable.name, "Test Consumable")
        self.assertEqual(consumable.description, "A test consumable")
        self.assertEqual(consumable.price, 50)
        self.assertEqual(consumable.effect, "heal")
        self.assertEqual(consumable.amount, 20)
        self.assertEqual(consumable.duration, 5)
        self.assertEqual(consumable.lvls.lvl, 1)
class TestWeaponList(unittest.TestCase):
    def test_weapon_init(self):
        weapon = weapons.Sword(name="Test Sword", description="A test sword", price=150, lvl=1, attack_power=30)
        self.assertEqual(weapon.name, "Test Sword")
        self.assertEqual(weapon.description, "A test sword")
        self.assertEqual(weapon.price, 150)
        self.assertEqual(weapon.attack_power, 30)
        self.assertEqual(weapon.lvls.lvl, 1)
class TestSaveLoad(unittest.TestCase):
    def test_save_character(self):
        char = character_creation.Character("TestChar", 1, 100)
        filename = "test_character.json"
        save_load.save_character(char, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_load_character(self):
        char = character_creation.Character("TestChar", 1, 100)
        filename = "test_character.json"
        save_load.save_character(char, filename)
        loaded_char = save_load.load_character(filename)
        self.assertEqual(loaded_char.name, "TestChar")
        self.assertEqual(loaded_char.lvls.lvl, 1)
        self.assertEqual(loaded_char.lvls.experience, 100)
        os.remove(filename)
    def test_load_character_not_found(self):
        filename = "non_existent_file.json"
        with self.assertRaises(FileNotFoundError):
            save_load.load_character(filename)
    def test_save_character_invalid(self):
        char = character_creation.Character("TestChar", 1, 100)
        filename = "test_character.json"
        with open(filename, "w") as f:
            f.write("Invalid JSON")
        with self.assertRaises(json.JSONDecodeError):
            save_load.load_character(filename)
        os.remove(filename)
class TestGenFunctions(unittest.TestCase):
    def test_random_number(self):
        num = gen.generate_random_number(1, 10)
        self.assertGreaterEqual(num, 1)
        self.assertLessEqual(num, 10)
    def test_random_choice(self):
        choices = ["a", "b", "c"]
        choice = gen.random_choice(choices)
        self.assertIn(choice, choices)
    def test_clear_screen(self):
        # This test is not practical to run in a unit test environment
        # but we can check if the function exists and runs without error
        try:
            gen.clear_screen()
        except Exception as e:
            self.fail(f"clear_screen raised {type(e).__name__} unexpectedly: {e}")
    def test_pause(self):
        # This test is not practical to run in a unit test environment
        # but we can check if the function exists and runs without error
        try:
            gen.pause()
        except Exception as e:
            self.fail(f"pause raised {type(e).__name__} unexpectedly: {e}")
if __name__ == "__main__":
    unittest.main()