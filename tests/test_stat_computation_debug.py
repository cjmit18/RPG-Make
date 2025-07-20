#!/usr/bin/env python3
"""
Debug stat computation with detailed logging.
"""

from game_sys.character.character_factory import create_character
from game_sys.magic.combo import ComboManager
from game_sys.core.scaling_manager import ScalingManager
from game_sys.logging import get_logger

logger = get_logger("stat_computation_debug")

def test_stat_computation_detailed():
    """Test detailed stat computation after combo."""
    print("=== Testing Detailed Stat Computation ===")
    
    # Create a player character
    player = create_character("hero", level=5)
    print(f"Player: {player.name}")
    
    # Get initial stats
    print(f"\nBefore combo:")
    initial_int = player.get_stat('intelligence')
    print(f"  Intelligence: {initial_int:.2f}")
    
    # Manually call compute_stat for magic_power before combo
    manual_magic_power_before = ScalingManager.compute_stat(player, 'magic_power')
    print(f"  Manual magic_power calculation: {manual_magic_power_before:.2f}")
    
    # Get magic_power via actor method
    actor_magic_power_before = player.get_stat('magic_power')
    print(f"  Actor magic_power: {actor_magic_power_before:.2f}")
    
    # Trigger steam combo
    print("\n--- Triggering Steam Combo ---")
    ComboManager.record_cast(player, "fireball")
    ComboManager.record_cast(player, "ice_shard")
    
    # Get stats after combo
    print(f"\nAfter combo:")
    final_int = player.get_stat('intelligence')
    print(f"  Intelligence: {final_int:.2f} ({final_int - initial_int:+.2f})")
    
    # Manually call compute_stat for magic_power after combo
    manual_magic_power_after = ScalingManager.compute_stat(player, 'magic_power')
    print(f"  Manual magic_power calculation: {manual_magic_power_after:.2f}")
    
    # Get magic_power via actor method
    actor_magic_power_after = player.get_stat('magic_power')
    print(f"  Actor magic_power: {actor_magic_power_after:.2f}")
    
    print(f"\nComparison:")
    print(f"  Magic power change (manual): {manual_magic_power_after - manual_magic_power_before:+.2f}")
    print(f"  Magic power change (actor): {actor_magic_power_after - actor_magic_power_before:+.2f}")
    
    # Check if there's a discrepancy
    if abs(manual_magic_power_after - actor_magic_power_after) > 0.01:
        print(f"  ⚠️  Discrepancy between manual calculation and actor method!")
        print(f"     This suggests caching or different computation paths")
    else:
        print(f"  ✅ Manual and actor calculations match")

if __name__ == "__main__":
    try:
        test_stat_computation_detailed()
        print("\n=== Debug Complete ===")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
