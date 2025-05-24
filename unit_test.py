"""
Pytest tests for the RPG game modules.
"""
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
import gen
import pytest

# Character Creation Tests
def test_player_init():
    player = character_creation.Player("TestChar", 1)
    assert player.name == "TestChar"
    assert player.lvls.lvl == 1
    assert player.lvls.experience == 0

def test_enemy_inheritance():
    enemy = character_creation.Enemy("Goblin", 1)
    assert isinstance(enemy, character_creation.Character)
    assert enemy.name == "Goblin"
    assert enemy.lvls.lvl == 1
    assert enemy.lvls.experience == 100

def test_enemy_init():
    enemy = character_creation.Enemy("Goblin", 1, 50)
    assert enemy.name == "Goblin"
    assert enemy.lvls.lvl == 1
    assert enemy.lvls.experience == 50

def test_enemy_experience():
    enemy = character_creation.Enemy("Goblin", 1, 50)
    assert enemy.lvls.experience == 50
    enemy.lvls.add_experience(100)
    assert enemy.lvls.experience == 150
    enemy.lvls.remove_experience(50)
    assert enemy.lvls.experience == 100

# Item Initialization Tests
def test_item_init():
    item = items.Item(name="Test Item", description="A test item", price=100, lvl=1)
    assert item.name == "Test Item"
    assert item.description == "A test item"
    assert item.price == 100
    assert item.lvls.lvl == 1

def test_consumable_init():
    consumable = items.Consumable(
        name="Test Consumable",
        description="A test consumable",
        price=50,
        effect="heal",
        amount=20,
        duration=5,
        lvl=1
    )
    assert consumable.name == "Test Consumable"
    assert consumable.description == "A test consumable"
    assert consumable.price == 50
    assert consumable.effect == "heal"
    assert consumable.amount == 20
    assert consumable.duration == 5
    assert consumable.lvls.lvl == 1

def test_potion_init():
    potion = potions.Health_Potion(
        name="Health Potion",
        description="Restores health",
        price=50,
        amount=20
    )
    assert potion.name == "Health Potion"
    assert potion.description == "Restores health"
    assert potion.price == 50
    assert potion.amount == 20

# Equipment Initialization Tests
def test_robe_init():
    robe = armors.Robe(
        name="Robe",
        description="Protective robe",
        price=100,
        defense_power=20,
        lvl=1
    )
    assert robe.lvl == 1
    assert robe.name == "Robe"
    assert robe.description == "Protective robe"
    assert robe.price == 100
    assert robe.defense_power == 20

def test_amulet_init():
    amulet = amulets.Amulet(
        name="Amulet",
        description="Protective amulet",
        price=200,
        effect="defense",
        lvl=1,
    )
    assert amulet.name == "Amulet"
    assert amulet.description == "Protective amulet"
    assert amulet.price == 200
    assert amulet.effect == "defense"
def test_ring_init():
    ring = rings.Ring(
        name="Ring",
        description="Magical ring",
        health_power=5,
        mana_power=10,
        stamina_power=3,
        lvl=1
    )
    assert ring.name == "Ring"
    assert ring.description == "Magical ring"
    assert ring.health_power == 5
    assert ring.mana_power == 10
    assert ring.stamina_power == 3
    assert ring.lvls.lvl == 1

def test_weapon_init():
    weapon = weapons.Sword(
        name="Test Sword",
        description="A test sword",
        price=150,
        lvl=1,
        attack_power=30
    )
    assert weapon.name == "Test Sword"
    assert weapon.description == "A test sword"
    assert weapon.price == 150
    assert weapon.attack_power == 30
    assert weapon.lvls.lvl == 1

def test_boots_init():
    boot = boots.Boot(
        name="Boots",
        description="Sturdy boots",
        price=80,
        speed_power=15,
        lvl=1
    )
    assert boot.name == "Boots"
    assert boot.description == "Sturdy boots"
    assert boot.price == 80
    assert boot.speed_power == 15
    assert boot.lvls.lvl == 1

# Class Creation Tests
def test_knight_class():
    char = character_creation.Character("KnightGuy")
    knight = class_creation.Knight(char)
    assert knight.job == "Knight"
    assert knight.character._base_stats.attack == 5

def test_mage_class():
    char = character_creation.Character("MageGuy")
    mage = class_creation.Mage(char)
    assert mage.job == "Mage"
    assert mage.character._base_stats.mana == 10

def test_rogue_class():
    char = character_creation.Character("RogueGuy")
    rogue = class_creation.Rogue(char)
    assert rogue.job == "Rogue"
    assert rogue.character._base_stats.attack == 5

def test_healer_class():
    char = character_creation.Character("HealerGuy")
    healer = class_creation.Healer(char)
    assert healer.job == "Healer"
    assert healer.character._base_stats.mana == 10

# Inventory Functions Tests
def test_inventory_add_remove():
    char = character_creation.Character("InvGuy")
    inv = inventory_functions.Inventory(char)
    item = items.Item(name="Potion")
    inv.add_item(item)
    assert item.id in inv.items
    inv.remove_item(item)
    assert item.id not in inv.items

def test_inventory_use_item():
    char = character_creation.Character("InvGuy")
    inv = inventory_functions.Inventory(char)
    potion = potions.Health_Potion(
        name="Health Potion",
        description="Restores health",
        price=50,
        amount=20
    )
    inv.add_item(potion)
    assert potion.id in inv.items
    inv.use_item(potion)
    assert potion.id not in inv.items

def test_inventory_list_counts():
    char = character_creation.Character("InvGuy")
    inv = inventory_functions.Inventory(char)
    assert len(inv.items) == 0
    item1 = items.Item(name="Potion")
    item2 = items.Item(name="Elixir")
    inv.add_item(item1)
    inv.add_item(item2)
    assert len(inv.items) == 2

# Experience & Leveling Tests
def test_levels_add_remove():
    char = character_creation.Enemy("ExpGuy", 0, 0)
    char.lvls.add_experience(50)
    assert char.lvls.experience == 50
    char.lvls.add_experience(100)
    assert char.lvls.experience == 150
    char.lvls.add_experience(200)
    assert char.lvls.experience == 350

def test_player_level_up():
    player = character_creation.Player("Hero", 1, 100)
    assert player.lvls.lvl == 1
    player.lvls.add_experience(100)
    assert player.lvls.lvl == 2
    assert player.lvls.experience == 0

# Generic Functions Tests
def test_random_number():
    num = gen.generate_random_number(1, 10)
    assert 1 <= num <= 10

def test_clear_screen():
    gen.clear_screen()
    # This test cannot be run in CI as it requires a terminal

@pytest.mark.skip(reason="pause() requires stdin, which is not available in CI")
def test_pause():
    gen.pause()
