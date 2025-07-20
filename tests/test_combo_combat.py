#!/usr/bin/env python3
"""
Test script to verify combo works in actual combat scenario.
"""

from game_sys.character.character_factory import create_character
from game_sys.combat.combat_service import CombatService
from game_sys.magic.combo import ComboManager
from game_sys.logging import get_logger

logger = get_logger("combo_combat_test")

def test_combo_in_combat():
    """Test that combo intelligence buff affects spell damage in combat."""
    print("=== Testing Combo Intelligence Buff in Combat ===")
    
    # Create player and enemy
    player = create_character("hero", level=5)
    enemy = create_character("goblin", level=3)
    
    print(f"Player: {player.name}")
    print(f"Enemy: {enemy.name}")
    
    # Get initial stats
    initial_int = player.get_stat('intelligence')
    initial_spell_power = player.get_stat('Magic_power')
    
    print(f"\nBefore combo:")
    print(f"  Intelligence: {initial_int:.2f}")
    print(f"  Magic Power: {initial_spell_power:.2f}")
    
    # Create combat service
    combat_service = CombatService()
    
    # Cast spell before combo
    print("\n--- Casting Fireball (before combo) ---")
    result1 = combat_service.cast_spell_at_target(player, "fireball", enemy)
    pre_combo_damage = result1.get('damage', 0)
    print(f"Damage before combo: {pre_combo_damage:.2f}")
    
    # Reset enemy health
    enemy.current_health = enemy.max_health
    
    # Trigger steam combo
    print("\n--- Triggering Steam Combo ---")
    ComboManager.record_cast(player, "fireball")
    ComboManager.record_cast(player, "ice_shard")
    
    # Get stats after combo
    final_int = player.get_stat('intelligence')
    final_spell_power = player.get_stat('Magic_power')
    
    print(f"\nAfter combo:")
    print(f"  Intelligence: {final_int:.2f} ({final_int - initial_int:+.2f})")
    print(f"  Magic Power: {final_spell_power:.2f} ({final_spell_power - initial_spell_power:+.2f})")
    
    # Cast spell after combo
    print("\n--- Casting Fireball (after combo) ---")
    result2 = combat_service.cast_spell_at_target(player, "fireball", enemy)
    post_combo_damage = result2.get('damage', 0)
    print(f"Damage after combo: {post_combo_damage:.2f}")
    
    print(f"\nDamage improvement: {post_combo_damage - pre_combo_damage:+.2f}")
    
    # Verify combo is actually helping
    if post_combo_damage > pre_combo_damage:
        print("✅ Combo intelligence buff is working!")
    else:
        print("❌ Combo intelligence buff may not be working properly")
        
    # Show active effects
    if hasattr(player, 'active_statuses'):
        print(f"\nActive effects: {list(player.active_statuses.keys())}")

if __name__ == "__main__":
    try:
        test_combo_in_combat()
        print("\n=== Combat Test Complete ===")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
