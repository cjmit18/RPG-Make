# game_sys/tests/test_inventory.py

import pytest
from game_sys.character.character_creation import Player
from game_sys.inventory.inventory import Inventory, get_equip_slot
from game_sys.items.item_base import Equipable, Item
from game_sys.items.consumable_list import Consumable


@pytest.fixture
def player():
    """
    Create a fresh Player with an empty inventory for each test.
    """
    p = Player(name="TestHero", level=1)
    # Clear any starting items
    p.inventory._items.clear()
    p.inventory._equipped_items = {slot: None for slot in p.inventory._equipped_items}
    p.inventory._equipped_item_objs.clear()
    return p


def test_add_and_auto_equip(player):
    """
    Adding an Equipable with auto_equip=True should equip exactly one copy,
    remove one from inventory, and place the rest (if any) in _items.
    """
    # Create a simple dagger Equipable and assign an ID
    dagger = Equipable(
        name="Test Dagger",
        description="A small dagger.",
        price=10,
        level=1,
        slot="weapon",
        bonuses={"attack": 2}
    )
    dagger.id = "dagger_id"

    # Add 3 copies, auto_equip=True
    player.inventory.add_item(dagger, quantity=3, auto_equip=True)

    # Expect: 1 equipped in slot "weapon", inventory has 2 left
    equipped = player.inventory.equipment["weapon"]
    assert equipped is not None and equipped.name == "Test Dagger"

    # Inventory should contain two copies
    inv_entry = player.inventory.items.get(dagger.id)
    assert inv_entry is not None
    assert inv_entry["quantity"] == 2


def test_equip_item_and_unequip_by_slot(player):
    """
    Manually equip an item by ID, then unequip by specifying the slot name.
    Inventory and equipment should update correctly.
    """
    sword = Equipable(
        name="Test Sword",
        description="A sharp sword.",
        price=25,
        level=1,
        slot="weapon",
        bonuses={"attack": 5}
    )
    sword.id = "sword_id"

    # Add 1 copy to inventory (not auto-equipped)
    player.inventory.add_item(sword, quantity=1, auto_equip=False)

    # Equip the sword
    player.inventory.equip_item(sword)
    # Now inventory[sword.id] should be removed
    assert sword.id not in player.inventory.items
    # Equipment slot "weapon" should hold this sword
    assert player.inventory.equipment["weapon"].name == "Test Sword"

    # Unequip by slot name
    player.inventory.unequip_item("weapon")
    # Equipment slot should now be empty
    assert player.inventory.equipment["weapon"] is None
    # Inventory should have exactly 1 copy back
    inv_entry = player.inventory.items.get(sword.id)
    assert inv_entry is not None and inv_entry["quantity"] == 1


def test_unequip_by_name_substring(player):
    """
    Equip an item and then unequip by passing a substring of its name.
    E.g., "dagger" should unequip "Test Dagger".
    """
    dagger = Equipable(
        name="Test Dagger",
        description="A small dagger.",
        price=10,
        level=1,
        slot="weapon",
        bonuses={"attack": 2}
    )
    dagger.id = "dagger_id"
    player.inventory.add_item(dagger, quantity=1, auto_equip=True)

    # Now the dagger is equipped; inventory should have 0 copies
    assert dagger.id not in player.inventory.items

    # Unequip by passing "dagger" (case-insensitive match)
    player.inventory.unequip_item("dagger")

    # Equipment slot should be empty
    assert player.inventory.equipment["weapon"] is None
    # Inventory should now contain 1 copy
    inv_entry = player.inventory.items.get(dagger.id)
    assert inv_entry is not None and inv_entry["quantity"] == 1


def test_equip_nonexistent_item_raises_keyerror(player):
    """
    Attempting to equip an item not in inventory should raise KeyError.
    """
    sword = Equipable(
        name="Test Sword",
        description="A sharp sword.",
        price=25,
        level=1,
        slot="weapon",
        bonuses={"attack": 5}
    )
    sword.id = "sword_id"
    with pytest.raises(KeyError):
        player.inventory.equip_item(sword.id)  # Not in inventory


def test_unequip_when_nothing_equipped_raises_valueerror(player):
    """
    Calling unequip_item on a slot that has nothing should raise ValueError.
    """
    with pytest.raises(ValueError):
        player.inventory.unequip_item("weapon")  # No weapon equipped


def test_use_consumable_reduces_quantity_and_applies_effect(player):
    """
    Using a Consumable item should apply its effect and reduce the inventory quantity by 1.
    """
    # Create a simple Health Potion that adds 50 HP and assign an ID
    class TestPotion(Consumable):
        def __init__(self):
            super().__init__(
                name="Test Potion",
                description="Restores 50 HP.",
                price=5,
                level=1,
                effect="health",
                amount=50,
                duration=0,
            )
            self.id = "potion_id"

    potion = TestPotion()
    # Ensure player current health is low
    max_hp = player.stats.effective()["health"]
    player.current_health = max_hp - 30

    # Add 2 potions to inventory
    player.inventory.add_item(potion, quantity=2)

    # Use one potion
    used = player.inventory.use_item(potion.id)
    assert used is True

    # Player health should have increased by 50 (capped at max)
    assert player.current_health == max_hp

    # Inventory quantity should have decreased by 1 (now 1 left)
    inv_entry = player.inventory.items.get(potion.id)
    assert inv_entry is not None and inv_entry["quantity"] == 1


def test_find_item_returns_none_when_not_present(player):
    """
    _find_item should return None if no matching ID or name is found.
    """
    result = player.inventory._find_item("nonexistent_id")
    assert result is None
    # Name substring test (no such item at all)
    result2 = player.inventory._find_item("nothing")
    assert result2 is None
