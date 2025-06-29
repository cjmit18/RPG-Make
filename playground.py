# playground.py
import asyncio
from game_sys.managers.time_manager import time_manager
from game_sys.effects.extensions import StatusEffect
from game_sys.effects.status_manager import status_manager
from game_sys.character.character_factory import create_character
from game_sys.core.scaling_manager import ScalingManager


def fmt(val: float) -> str:
    s = f"{val:.2f}"
    return s.rstrip('0').rstrip('.') if '.' in s else s


async def demo():
    # Start the global async time manager (ticks at 60Hz)
    time_manager.start(interval=1/60)

    # Create hero and goblin actors via the factory
    hero   = create_character('hero')
    goblin = create_character('goblin')

    # Register actors for pool regen and status ticking
    time_manager.register(hero)
    time_manager.register(goblin)
    status_manager.register_actor(goblin)

    # Equip hero with a basic weapon
    class Weapon:
        def __init__(self, dmg):
            self.base_damage = dmg
            self.effect_ids = []
    hero.equip_weapon(Weapon(20))

    # Show goblin HP before damage
    print(f"Goblin HP before damage: {fmt(goblin.current_health)}")
    # Compute and apply direct damage
    dmg = ScalingManager.compute_damage(hero, goblin, hero.weapon)
    goblin.take_damage(dmg, hero)
    print(f"Goblin HP after direct damage: {fmt(goblin.current_health)}")

    # Apply a poison status: 3s duration, 1 HP/sec
    poison = StatusEffect(name='poison', duration=3.0, tick_damage=1.0)
    poison.apply(hero, goblin)
    print("Applied poison to Goblin (3s @1 HP/s)")

    # Wait 4 seconds to allow poison ticks and regen
    await asyncio.sleep(4)

    print(f"Goblin HP after poison ticks: {fmt(goblin.current_health)}")

    # Clean up the time manager
    time_manager.stop()

if __name__ == '__main__':
    asyncio.run(demo())
if __name__ == "__main__":
    # Run each test in sequence
    # view_character_test()
    # learning_system_test()
    # inventory_system_test()
     combat_system_test()
