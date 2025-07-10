import asyncio
import pytest
from game_sys.character.actor import Actor, Player, Enemy
from game_sys.items.item_loader import load_item

@pytest.mark.asyncio
async def test_actor_async_save_load(tmp_path):
    # Create an actor and modify state
    actor = Actor("TestHero", {"health": 100, "mana": 50, "stamina": 30})
    actor.level = 5
    actor.xp = 1234
    actor.gold = 99
    actor.current_health = 77
    actor.current_mana = 33
    actor.current_stamina = 22
    # Add inventory
    potion = load_item("healing_potion")
    if potion:
        actor.inventory.add_item(potion)
    # Save async
    save_path = tmp_path / "actor_save.json"
    await actor.save_async(str(save_path))
    # Change state
    actor.level = 1
    actor.xp = 0
    actor.gold = 0
    actor.current_health = 1
    actor.inventory.clear()
    # Load async
    await actor.load_async(str(save_path))
    # Check restored state
    assert actor.level == 5
    assert actor.xp == 1234
    assert actor.gold == 99
    assert actor.current_health == 77
    assert actor.current_mana == 33
    assert actor.current_stamina == 22
    if potion:
        assert any(item.id == potion.id for item in actor.inventory.list_items())

@pytest.mark.asyncio
async def test_player_async_save_load(tmp_path):
    player = Player("AsyncPlayer", {"health": 120, "mana": 80})
    player.level = 3
    player.xp = 555
    player.gold = 42
    save_path = tmp_path / "player_save.json"
    await player.save_async(str(save_path))
    player.level = 1
    player.xp = 0
    await player.load_async(str(save_path))
    assert player.level == 3
    assert player.xp == 555
    assert player.gold == 42

@pytest.mark.asyncio
async def test_enemy_async_save_load(tmp_path):
    enemy = Enemy("AsyncEnemy", {"health": 80, "mana": 10})
    enemy.level = 2
    enemy.xp = 99
    enemy.gold = 7
    save_path = tmp_path / "enemy_save.json"
    await enemy.save_async(str(save_path))
    enemy.level = 1
    enemy.xp = 0
    await enemy.load_async(str(save_path))
    assert enemy.level == 2
    assert enemy.xp == 99
    assert enemy.gold == 7

@pytest.mark.asyncio
async def test_async_inventory_equipment(tmp_path):
    actor = Actor("EquipHero", {"health": 100})
    sword = load_item("iron_sword")
    shield = load_item("wooden_shield")
    if sword:
        actor.equip_weapon(sword)
    if shield:
        actor.equip_offhand(shield)
    save_path = tmp_path / "equip_save.json"
    await actor.save_async(str(save_path))
    # Remove equipment
    actor.unequip_weapon()
    actor.unequip_offhand()
    await actor.load_async(str(save_path))
    # Equipment should be restored
    if sword:
        assert actor.weapon and actor.weapon.id == sword.id
    if shield:
        assert actor.offhand and actor.offhand.id == shield.id
