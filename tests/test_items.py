import pytest
from game_sys.items.factory import create_item, list_all_ids

def test_create_valid_item_and_id():
    for item_id in list_all_ids():
        item = create_item(item_id)
        assert hasattr(item, "id") and item.id == item_id
        # name and description must be non-empty
        assert getattr(item, "name", "")
        assert getattr(item, "description", "")

def test_missing_template_raises():
    with pytest.raises(KeyError):
        create_item("does_not_exist")

def test_ranged_bonus_consistency(monkeypatch):
    # force RNG to always return min for deterministic test
    class DummyRNG:
        def __init__(self): pass
        def randint(self, a, b): return a

    # pick an item known to have ranged bonus, e.g. iron_sword
    sword = create_item("iron_sword", rng=DummyRNG())
    assert sword.bonuses["attack"] == 3  # matches min
