import re
import pytest

from core.actor import Actor
from core.combat_functions import CombatCapabilities
from core.inventory_functions import Inventory
from core.experience_functions import Levels
from items.items_list import Item, Consumable

# --- Helpers -----------------------------------------------------------------

class DummyRNG:
    """Fake RNG returning fixed values for uniform, random, and randint."""
    def __init__(self, uniform_value, random_value, randint_value):
        self.uniform_value = uniform_value
        self.random_value = random_value
        self.randint_value = randint_value

    def uniform(self, a, b):
        return self.uniform_value

    def random(self):
        return self.random_value

    def randint(self, a, b):
        return self.randint_value

def extract_damage(text: str) -> int:
    """Pull out the damage integer from a string like 'Hero deals 6 damage.'"""
    m = re.search(r"deals (\d+) damage", text)
    assert m, f"No damage found in '{text}'"
    return int(m.group(1))


# --- Actor & Stats Tests ----------------------------------------------------

def test_actor_initial_stats_and_resources():
    # At level=2, Base job gives 3*lvl = 6 for all stats
    a = Actor("Test", level=2)
    assert a.attack == 6
    assert a.defense == 6
    assert a.speed == 6
    # Health/mana/stamina start full
    assert a.health == a.max_health == 6
    assert a.mana   == a.max_mana   == 6
    assert a.stamina== a.max_stamina== 6

def test_leveling_up_resets_experience_and_increases_level():
    a = Actor("Lev", level=1, experience=0)
    levels: Levels = a.levels
    # Add just under the threshold → no level up
    levels.add_experience(levels.required_experience() - 1)
    assert levels.lvl == 1
    # Add enough for exactly one level up
    levels.add_experience(1)
    assert levels.lvl == 2
    assert levels.experience == 0


# --- CombatTests -------------------------------------------------------------

def test_calculate_damage_no_crit_with_dummy_rng():
    """
    With uniform=1.0 and random()=1.0 (no crit),
    base = 3 - 3*0.05 = 2.85 → round → 3.
    """
    rng = DummyRNG(uniform_value=1.0, random_value=1.0, randint_value=1)
    p = Actor("Attacker", level=1)
    e = Actor("Defender", level=1)
    combat = CombatCapabilities(p, e, rng=rng)
    out = combat.calculate_damage(p, e)
    assert extract_damage(out) == 3
    assert "Critical Hit!" not in out

def test_calculate_damage_with_crit_and_dummy_rng():
    """
    With uniform=1.0 and random()=0.0 (crit),
    base*2 = 2.85*2 = 5.7 → round → 6.
    """
    rng = DummyRNG(uniform_value=1.0, random_value=0.0, randint_value=1)
    p = Actor("Attacker", level=1)
    e = Actor("Defender", level=1)
    combat = CombatCapabilities(p, e, rng=rng)
    out = combat.calculate_damage(p, e)
    assert extract_damage(out) == 6
    assert "Critical Hit!" in out

def test_start_combat_loop_terminates_and_returns_winner():
    """
    Using a DummyRNG that always deals exactly max damage,
    and an action_fn that always attacks, the loop ends immediately.
    """
    rng = DummyRNG(uniform_value=1.0, random_value=1.0, randint_value=1)
    p = Actor("Hero", level=1)
    e = Actor("Goblin", level=1)
    combat = CombatCapabilities(p, e, rng=rng, action_fn=lambda actor: "attack")
    result = combat.start_combat_loop()
    assert result == "Hero wins!"


# --- Inventory Tests --------------------------------------------------------

def test_inventory_add_and_remove():
    inv: Inventory = Actor("InvGuy", level=1).inventory
    item = Item(name="TestItem", description="desc", price=1, lvl=1)
    inv.add_item(item, quantity=2)
    assert item.id in inv.items
    assert inv.items[item.id]["quantity"] == 2

    inv.remove_item(item)
    assert inv.items[item.id]["quantity"] == 1

    inv.remove_item(item)
    assert item.id not in inv.items

def test_use_consumable_item_restores_health():
    # Put actor at 0 health, then use a healing consumable
    a = Actor("Healee", level=1)
    a.health = 0
    potion = Consumable(
        name="HealPotion",
        description="Heals 1 hp",
        price=0,
        effect="health",
        amount=1,
        duration=1,
        lvl=1
    )
    inv = a.inventory
    inv.add_item(potion, quantity=1)
    inv.use_item(potion)
    assert a.health > 0


# --- Edge & Error Cases -----------------------------------------------------

def test_remove_nonexistent_item_raises():
    inv = Inventory(Actor("X",1))
    fake = Item(name="Fake")
    with pytest.raises(ValueError):
        inv.remove_item(fake)

def test_use_non_consumable_raises_type_error():
    inv = Inventory(Actor("X",1))
    sword = Item(name="NotAConsumable")
    inv.add_item(sword)
    with pytest.raises(TypeError):
        inv.use_item(sword)
