"""
Pytest tests for the RPG game modules.
"""
import random
import re
import core.character_creation as character_creation
import core.inventory_functions as inventory_functions
import core.combat_functions as combat_functions
from items import items_list as items, potion_list as potions, armor_list as armors, amulet_list as amulets, weapon_list as weapons, ring_list as rings, boots_list as boots
from jobs import Base, Knight, Mage, Rogue, Healer
import core.experience_functions as experience_functions
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
    assert isinstance(enemy, character_creation.Enemy)    
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
    assert robe.lvls.lvl == 1
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
    knight = Knight(char)
    assert knight.job == "Knight"
    assert knight.base_stats(1)["attack"] == 5
    assert knight.base_stats(1)["defense"] == 7
    assert knight.base_stats(1)["speed"] == 3
    assert knight.base_stats(1)["health"] == 10
    assert knight.base_stats(1)["mana"] == 2
    assert knight.base_stats(1)["stamina"] == 5
def test_mage_class():
    char = character_creation.Character("MageGuy")
    mage = Mage(char)
    assert mage.job == "Mage"
    assert mage.base_stats(1)["attack"] == 8
    assert mage.base_stats(1)["defense"] == 2
    assert mage.base_stats(1)["speed"] == 3
    assert mage.base_stats(1)["health"] == 7
    assert mage.base_stats(1)["mana"] == 7
    assert mage.base_stats(1)["stamina"] == 5
def test_rogue_class():
    char = character_creation.Character("RogueGuy")
    rogue = Rogue(char)
    assert rogue.job == "Rogue"
    assert rogue.base_stats(1)["attack"] == 5
    assert rogue.base_stats(1)["defense"] == 2
    assert rogue.base_stats(1)["speed"] == 8
    assert rogue.base_stats(1)["health"] == 7
    assert rogue.base_stats(1)["mana"] == 2
    assert rogue.base_stats(1)["stamina"] == 8
def test_healer_class():
    char = character_creation.Character("HealerGuy")
    healer = Healer(char)
    assert healer.job == "Healer"
    assert healer.base_stats(1)["attack"] == 5
    assert healer.base_stats(1)["defense"] == 2
    assert healer.base_stats(1)["speed"] == 3
    assert healer.base_stats(1)["health"] == 10
    assert healer.base_stats(1)["mana"] == 7
    assert healer.base_stats(1)["stamina"] == 5
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
    assert char.lvls.experience == 150
    char.lvls.add_experience(100)
    assert char.lvls.experience == 250

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
def extract_damage(text: str) -> int:
    """
    Pull out the damage integer from a string like
    "Hero deals 6 damage." or "Hero deals 13 damage. Critical Hit!"
    """
    m = re.search(r"deals (\d+) damage", text)
    assert m, f"No damage found in '{text}'"
    return int(m.group(1))


def test_combat_deterministic_with_seed():
    # 1) Seed RNG and run two rolls
    rng1 = random.Random(123)
    p1 = character_creation.Player("Hero", level=1)
    e1 = character_creation.Enemy("Goblin", level=1)
    combat1 = combat_functions.Combat(p1, e1, rng1)

    out1 = combat1.calculate_damage(p1, e1)
    out2 = combat1.calculate_damage(p1, e1)

    # 2) Reset RNG to same seed, new combat instance
    rng2 = random.Random(123)
    p2 = character_creation.Player("Hero", level=1)
    e2 = character_creation.Enemy("Goblin", level=1)
    combat2 = combat_functions.Combat(p2, e2, rng2)

    out1b = combat2.calculate_damage(p2, e2)
    out2b = combat2.calculate_damage(p2, e2)

    # 3) Compare only the damage numbers
    assert extract_damage(out1) == extract_damage(out1b)
    assert extract_damage(out2) == extract_damage(out2b)


class DummyRNG:
    """A fake RNG that returns fixed values for uniform, random, and randint."""
    def __init__(self, uniform_value, random_value, randint_value):
        self.uniform_value = uniform_value
        self.random_value  = random_value
        self.randint_value = randint_value

    def uniform(self, a, b):
        return self.uniform_value

    def random(self):
        return self.random_value

    def randint(self, a, b):
        return self.randint_value


def test_calculate_damage_no_crit_with_dummy_rng():
    # force multiplier=1.0 (no change), random()=1.0 (no crit)
    rng = DummyRNG(uniform_value=1.0, random_value=1.0, randint_value=1)
    p = character_creation.Player("TestNoCrit", level=1)
    e = character_creation.Enemy("Dummy", level=1)
    combat = combat_functions.Combat(p, e, rng)

    result = combat.calculate_damage(p, e)
    damage = extract_damage(result)
    # Base calc: (5 - 0.05*2) = 4.9 → round(4.9) = 5
    assert damage == 5
    assert "Critical Hit!" not in result


def test_calculate_damage_with_crit_and_dummy_rng():
    # force multiplier=1.0, random()=0.0 (crit)
    rng = DummyRNG(uniform_value=1.0, random_value=0.0, randint_value=1)
    p = character_creation.Player("TestCrit", level=1)
    e = character_creation.Enemy("Dummy", level=1)
    combat = combat_functions.Combat(p, e, rng)

    result = combat.calculate_damage(p, e)
    damage = extract_damage(result)
    # Crit doubles 4.9 → 9.8 → round(9.8) = 10
    assert damage == 10
    assert "Critical Hit!" in result
@pytest.mark.skip(reason="pause() requires stdin, which is not available in CI")
def test_pause():
    gen.pause()
