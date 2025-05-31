# game_sys/tests/test_loot.py

import pytest
import random
import importlib
from game_sys.character.character_creation import Enemy, Player
from game_sys.combat.combat import CombatCapabilities, DROP_TABLES
from game_sys.items.item_base import Equipable


class DeterministicRNG(random.Random):
    """RNG that always returns a fixed float for random() and a fixed int for randint()."""
    def __init__(self, fixed_random: float, fixed_randint: int):
        super().__init__()
        self._fixed_random = fixed_random
        self._fixed_randint = fixed_randint

    def random(self):
        return self._fixed_random

    def randint(self, a, b):
        return self._fixed_randint


@pytest.fixture(autouse=True)
def patch_rusty_dagger(monkeypatch):
    """
    Monkey‐patch create_item in game_sys.combat.combat so that create_item("rusty_dagger")
    returns a minimal Equipable with a stable .id.
    """
    combat_mod = importlib.import_module("game_sys.combat.combat")

    def fake_create_item(item_id: str, rng=None):
        if item_id == "rusty_dagger":
            dagger = Equipable(
                name="Rusty Dagger",
                description="A basic rusty dagger.",
                price=0,
                level=1,
                slot="weapon",
                bonuses={"attack": 1}
            )
            dagger.id = "rusty_dagger"
            return dagger
        else:
            real_ci = importlib.import_module("game_sys.items.factory").create_item
            return real_ci(item_id, rng)

    monkeypatch.setattr(
        combat_mod,
        "create_item",
        fake_create_item,
        raising=True
    )
    yield
    # monkeypatch undone automatically


@pytest.fixture(autouse=True)
def ensure_drop_table_for_goblin():
    """
    Temporarily overwrite DROP_TABLES["goblin"] so that:
    - The only drop entry is: always (chance=1.0) 2×"rusty_dagger".
    """
    combat_mod = importlib.import_module("game_sys.combat.combat")
    original = DROP_TABLES.get("goblin")

    DROP_TABLES["goblin"] = [
        (lambda tid="rusty_dagger", cm=combat_mod: cm.create_item(tid), 1.0, 2, 2)
    ]
    yield
    # Restore original after test
    if original is None:
        DROP_TABLES.pop("goblin", None)
    else:
        DROP_TABLES["goblin"] = original


def test_roll_loot_only_json_drops_for_enemy():
    """
    An Enemy with job_id "goblin" should drop only via DROP_TABLES,
    never from its own inventory (which we leave untouched).
    """
    goblin = Enemy(name="GoblinBoss", level=1)
    goblin.assign_job_by_id("goblin")

    rng = DeterministicRNG(fixed_random=0.0, fixed_randint=2)
    dummy_hero = Player(name="Dummy", level=1)
    combat = CombatCapabilities(character=dummy_hero, enemy=goblin, rng=rng)

    drops = combat.roll_loot(goblin)
    assert len(drops) == 1
    item_obj, qty = drops[0]
    assert isinstance(item_obj, Equipable)
    assert item_obj.name == "Rusty Dagger"
    assert qty == 2


def test_transfer_loot_adds_to_winner_inventory():
    """
    Given the patched drop table for "goblin", transfer_loot should:
      - Give exactly 2 rusty daggers to the winner’s inventory.
      - Not modify the goblin’s original inventory contents.
    """
    hero = Player(name="Hero", level=1)
    goblin = Enemy(name="GoblinBoss", level=1)
    goblin.assign_job_by_id("goblin")

    # Record hero’s inventory IDs before looting
    before_hero_ids = set(hero.inventory.items.keys())
    # Record goblin’s inventory state (keys and quantities) before looting
    before_goblin_state = {iid: slot["quantity"] for iid, slot in goblin.inventory.items.items()}

    rng = DeterministicRNG(fixed_random=0.0, fixed_randint=2)
    combat = CombatCapabilities(character=hero, enemy=goblin, rng=rng)

    combat.transfer_loot(winner=hero, defeated=goblin)

    after_hero_ids = set(hero.inventory.items.keys())
    new_ids = after_hero_ids - before_hero_ids
    assert len(new_ids) == 1

    new_id = next(iter(new_ids))
    slot = hero.inventory.items[new_id]
    assert slot["quantity"] == 2
    assert slot["item"].name == "Rusty Dagger"

    # Verify goblin’s inventory remains unchanged
    after_goblin_state = {iid: slot["quantity"] for iid, slot in goblin.inventory.items.items()}
    assert after_goblin_state == before_goblin_state
