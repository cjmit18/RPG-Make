"""Test buffs applied by consumables."""
import pytest
from game_sys.character.character_creation import Player
from game_sys.items.factory import create_item
from game_sys.combat.status import StatusEffect


@pytest.fixture
def player():
    """
    Create a fresh Player for testing buffs.
    """
    p = Player(name="BuffTester", level=1)
    # Clear any starting items so stats are predictable
    p.inventory._items.clear()
    p.inventory._equipped_items = {slot: None for slot in p.inventory._equipped_items}
    p.inventory._equipped_item_objs.clear()
    # Ensure no active buffs
    p.status_effects.clear()
    return p


def test_temporary_attack_buff_via_consumable(player):
    """
    Using the 'empower_potion' (attack +5 for 3 turns) should:
      - Immediately increase player.attack by +5
      - Maintain the buff for exactly 3 ticks
      - Expire thereafter, returning attack to base
    """
    # 1) Determine base attack
    base_attack = player.attack

    # 2) Create and add the empower potion
    potion = create_item("empower_potion")
    assert potion.effect == "attack"
    assert potion.amount == 5
    assert potion.duration == 3

    player.inventory.add_item(potion, quantity=1)

    # 3) Use the potion
    used = player.inventory.use_item(potion.id)
    assert used is True

    # After use, there should be exactly one StatusEffect
    assert len(player.status_effects) == 1
    effect: StatusEffect = player.status_effects[0]
    assert effect.stat_mods.get("attack", 0) == 5
    assert effect.duration == 3

    # 4) Immediately after consuming, attack should be base + 5
    assert player.attack == base_attack + 5

    # 5) Tick once: duration -> 2; attack still base + 5
    for eff in list(player.status_effects):
        eff.tick()
        if eff.is_expired():
            player.status_effects.remove(eff)
    assert len(player.status_effects) == 1
    assert player.status_effects[0].duration == 2
    assert player.attack == base_attack + 5

    # 6) Tick twice more: after second tick (duration -> 1): still buffed
    for eff in list(player.status_effects):
        eff.tick()
        if eff.is_expired():
            player.status_effects.remove(eff)
    assert len(player.status_effects) == 1
    assert player.status_effects[0].duration == 1
    assert player.attack == base_attack + 5

    # 7) Tick third time: effect expires (duration -> 0), then removed
    for eff in list(player.status_effects):
        eff.tick()
        if eff.is_expired():
            player.status_effects.remove(eff)
    assert len(player.status_effects) == 0

    # Attack should now be back to base
    assert player.attack == base_attack
