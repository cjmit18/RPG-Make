#!/usr/bin/env python3
"""
Debug Magic Power calculation after combo.
"""

from game_sys.character.character_factory import create_character
from game_sys.magic.combo import ComboManager
from game_sys.logging import get_logger

logger = get_logger("magic_power_debug")

def test_magic_power_calculation():
    """Test Magic Power calculation after combo."""
    print("=== Testing Magic Power Calculation ===")
    
    # Create a player character
    player = create_character("hero", level=5)
    print(f"Player: {player.name}")
    
    # Get initial stats
    print(f"\nBefore combo:")
    initial_int = player.get_stat('intelligence')
    initial_magic_power = player.get_stat('magic_power')
    print(f"  Intelligence: {initial_int:.2f}")
    print(f"  Magic Power: {initial_magic_power:.2f}")
    
    # Check base stats vs computed stats
    base_int = player.base_stats.get('intelligence', 0)
    print(f"  Base Intelligence: {base_int:.2f}")
    
    # Trigger steam combo
    print("\n--- Triggering Steam Combo ---")
    ComboManager.record_cast(player, "fireball")
    ComboManager.record_cast(player, "ice_shard")
    
    # Get stats after combo
    print(f"\nAfter combo:")
    final_int = player.get_stat('intelligence')
    final_magic_power = player.get_stat('magic_power')
    print(f"  Intelligence: {final_int:.2f} ({final_int - initial_int:+.2f})")
    print(f"  Magic Power: {final_magic_power:.2f} ({final_magic_power - initial_magic_power:+.2f})")
    
    # Check if the issue is with magic_power derivation
    print(f"\nDebugging magic_power derivation:")
    
    # Test manual calculation
    from game_sys.config.config_manager import ConfigManager
    cfg = ConfigManager()
    magic_power_mult = cfg.get('constants.derived_stats.magic_power', 1.0)
    print(f"  Magic Power multiplier from config: {magic_power_mult}")
    
    expected_magic_power = final_int * magic_power_mult
    print(f"  Expected Magic Power (int * mult): {expected_magic_power:.2f}")
    print(f"  Actual Magic Power: {final_magic_power:.2f}")
    
    # Check if magic_power is being computed correctly
    if abs(expected_magic_power - final_magic_power) > 0.01:
        print(f"  ⚠️  Magic Power mismatch!")
    else:
        print(f"  ✅ Magic Power calculation is correct")

if __name__ == "__main__":
    try:
        test_magic_power_calculation()
        print("\n=== Debug Complete ===")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
