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
import character_creation
import inventory_functions
import combat_functions
import items_list as items
import experience_functions
import class_creation
import gen

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

    def test_enemy_inheritance(self):
        enemy = character_creation.Enemy("Goblin", 1)
        self.assertIsInstance(enemy, character_creation.Character)
        self.assertEqual(enemy.name, "Goblin")

class TestItemsList(unittest.TestCase):
    def test_item_init(self):
        item = items.Item(name="Sword", description="Sharp blade", price=100, lvl=2)
        self.assertEqual(item.name, "Sword")
        self.assertEqual(item.description, "Sharp blade")
        self.assertEqual(item.price, 100)
        self.assertEqual(item.lvl, 2)

    def test_consumable_inheritance(self):
        consumable = items.Consumable(name="Food", effect="heal", amount=5)
        self.assertIsInstance(consumable, items.Item)
        self.assertEqual(consumable.effect, "heal")
        self.assertEqual(consumable.amount, 5)

class TestClassCreation(unittest.TestCase):
    def test_knight_class(self):
        char = character_creation.Character("KnightGuy")
        knight = class_creation.Knight(char)
        self.assertEqual(knight.class_, "Knight")
        self.assertEqual(knight.attack, 5)

    def test_mage_class(self):
        char = character_creation.Character("MageGuy")
        mage = class_creation.Mage(char)
        self.assertEqual(mage.class_, "Mage")
        self.assertEqual(mage.mana, 10)

class TestExperienceFunctions(unittest.TestCase):
    def test_levels(self):
        char = character_creation.Character("LevelGuy", 5, 200)
        levels = experience_functions.Levels(char, 5, 200)
        self.assertEqual(levels.lvl, 5)
        self.assertEqual(levels.experience, 200)

class TestInventoryFunctions(unittest.TestCase):
    def test_inventory_add(self):
        char = character_creation.Character("InvGuy")
        inv = inventory_functions.Inventory(char)
        item = items.Item(name="Potion")
        inv.add_item(item)
        self.assertIn(item.id, inv.items)

class TestCombatFunctions(unittest.TestCase):
    def test_attack(self):
        attacker = character_creation.Character("Attacker", 1)
        defender = character_creation.Character("Defender", 1)
        # Assuming combat_functions.attack returns damage dealt
        if hasattr(combat_functions, "attack"):
            result = combat_functions.attack(attacker, defender)
            self.assertIsInstance(result, int)

if __name__ == "__main__":
    unittest.main()