# playground.py

import asyncio
from game_sys.core.version import __version__
from game_sys.managers.time_manager import time_manager
from game_sys.effects.extensions import StatusEffect
from game_sys.effects.status_manager import status_manager
from game_sys.character.character_factory import create_character
from game_sys.items.item_loader import load_item
from game_sys.skills.skill_loader import load_skill
from game_sys.magic.spell_loader import load_spell
from game_sys.core.scaling_manager import ScalingManager

def fmt(val: float) -> str:
    """No decimals if integer, else two decimal places."""
    s = f"{val:.2f}"
    return s[:-3] if s.endswith(".00") else s.rstrip("0").rstrip(".")

async def demo():
    print(f"▶ Game version: {__version__}\n")

    # 1) Start the clock
    time_manager.start(interval=1/60)

    # 2) Create our actors
    hero   = create_character('hero')
    goblin = create_character('goblin')

    # 3) Register them
    time_manager.register(hero)
    time_manager.register(goblin)
    status_manager.register_actor(goblin)

    # 4) Load & equip items
    potion  = load_item('potion_health')
    sword   = load_item('iron_sword')
    armor   = load_item('leather_armor')
    enchant = load_item('fire_enchant')

    hero.equip_weapon(sword)
    armor.apply(hero)
    enchant.apply(hero, sword)

    print("Sword.effect_ids:",   sword.effect_ids)
    print("Sword.enchantments:", sword.enchantments, "\n")

    # 5) Hero takes damage, uses potion
    print(f"Hero HP before damage: {fmt(hero.current_health)}")
    hero.take_damage(30)
    print(f"Hero HP after 30 dmg:     {fmt(hero.current_health)}")

    hero.inventory.add_item(potion)
    print("Inventory before potion:", [i.id for i in hero.inventory.list_items()])

    hero.use_item('potion_health')
    print(f"Hero HP after potion:     {fmt(hero.current_health)}")
    print("Inventory after potion: ", [i.id for i in hero.inventory.list_items()], "\n")

    # 6) Hero attacks Goblin
    print(f"Goblin HP before attack: {fmt(goblin.current_health)}")
    dmg = ScalingManager.compute_damage(hero, goblin, hero.weapon)
    goblin.take_damage(dmg, hero)
    print(f"Goblin took {fmt(dmg)} dmg → HP now: {fmt(goblin.current_health)}\n")
    goblin.current_health = goblin.max_health  # Reset for next actions
    # 7) Use a skill
    used = await hero.use_skill('cleave', goblin)
    if used:
        print(f"Goblin HP after Cleave:   {fmt(goblin.current_health)}\n")
    else:
        print("Cleave failed (no stamina or on cooldown)\n")
    goblin.current_health = goblin.max_health  # Reset for next actions
    # 8) Cast a spell
    print(f"Goblin HP before Fireball: {fmt(goblin.current_health)}")
    cast = await hero.cast_spell('fireball', goblin)

    if cast:
        print("Casting Fireball…")  # wait for DOTs / ticks
        print(f"Goblin HP after fireball: {fmt(goblin.current_health)}\n")
        await asyncio.sleep(5)
        print(f"Goblin HP after Fireball DOT: {fmt(goblin.current_health)}")
    else:
        print("Fireball failed (no mana or on cooldown)\n")
    goblin.current_health = goblin.max_health  # Reset for next actions
    # 9) Apply poison status
    poison = StatusEffect(name='poison', duration=3.0, tick_damage=1.0)
    poison.apply(hero, goblin)
    print("Applied Poison (3s @1 HP/s)…")
    await asyncio.sleep(4)
    print(f"Goblin HP after Poison:    {fmt(goblin.current_health)}\n")

    # 10) Stop the clock
    time_manager.stop()

if __name__ == '__main__':
    asyncio.run(demo())
# This is a simple playground script to demonstrate the game engine's features.
