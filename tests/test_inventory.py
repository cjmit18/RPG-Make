import pytest
from game_sys.items.factory import create_item
from game_sys.core.actor import Actor
from game_sys.items.item_base import Item
def test_add_remove_and_equip():
    hero = Actor("Bob", level=1)
    sword = create_item("iron_sword")
    hero.inventory.add_item(sword, quantity=2)
    assert hero.inventory.items[sword.id]["quantity"] == 2

    hero.inventory.equip_item(sword.id)
    assert hero.inventory.equipment["weapon"].id == sword.id
    # quantity reduced by 1
    assert hero.inventory.items[sword.id]["quantity"] == 1

    hero.inventory.unequip_item("weapon")
    assert hero.inventory.equipment["weapon"] is None
    # returned to bag
    assert hero.inventory.items[sword.id]["quantity"] == 2

def test_use_consumable_and_errors():
    hero = Actor("Cindy", level=1)
    potion = create_item("health_potion")
    # add two potions
    hero.inventory.add_item(potion, quantity=2)
    # deplete health to test heal
    hero.current_health = 1
    hero.inventory.use_item(potion)
    assert hero.current_health > 1
    # only one left
    assert hero.inventory.items[potion.id]["quantity"] == 1

    # using on non-consumable raises
    sword = create_item("iron_sword")
    hero.inventory.add_item(sword)
    with pytest.raises(TypeError):
        hero.inventory.use_item(sword)

    # removing when none left raises
    fake = Item(name="Fake", description="", price=0, level=1)
    with pytest.raises(ValueError):
        hero.inventory.use_item(fake)
