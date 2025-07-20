#!/usr/bin/env python3
"""
Test script to debug combo intelligence buff issue.
"""

from game_sys.character.character_factory import create_character
from game_sys.magic.combo import ComboManager
from game_sys.logging import get_logger

logger = get_logger("combo_debug")

def test_combo_intelligence_buff():
    """Test if intelligence is properly increased after steam combo."""
    print("=== Testing Steam Combo Intelligence Buff ===")
    
    # Create a player character
    player = create_character("hero", level=5)
    print(f"Player: {player.name}")
    
    # Get initial intelligence
    initial_int = player.get_stat('intelligence')
    print(f"Initial Intelligence: {initial_int:.2f}")
    
    # Check initial stat_bonus_ids and active_statuses
    print(f"Initial stat_bonus_ids: {getattr(player, 'stat_bonus_ids', [])}")
    print(f"Initial active_statuses: {list(getattr(player, 'active_statuses', {}).keys())}")
    
    # Trigger steam combo by recording spell casts
    print("\n--- Casting Fireball ---")
    ComboManager.record_cast(player, "fireball")
    
    print("--- Casting Ice Shard ---")
    ComboManager.record_cast(player, "ice_shard")
    
    # Check if combo was triggered
    print(f"\nAfter combo - stat_bonus_ids: {getattr(player, 'stat_bonus_ids', [])}")
    print(f"After combo - active_statuses: {list(getattr(player, 'active_statuses', {}).keys())}")
    
    # Get intelligence after combo
    final_int = player.get_stat('intelligence')
    print(f"Final Intelligence: {final_int:.2f}")
    print(f"Intelligence Change: {final_int - initial_int:+.2f}")
    
    # Check if buff is actually applied
    if hasattr(player, 'active_statuses'):
        for eff_id, (eff, duration) in player.active_statuses.items():
            print(f"Active effect: {eff_id} -> {type(eff).__name__}")
            if hasattr(eff, 'stat'):
                print(f"  Target stat: {eff.stat}")
                print(f"  Amount: {eff.amount}")
                print(f"  Duration: {duration}")
                
                # Test the modify_stat method directly
                print(f"  Testing modify_stat for intelligence:")
                test_result = eff.modify_stat(initial_int, player, 'intelligence')
                print(f"    Direct call result: {test_result}")
                
                print(f"  Testing modify_stat for strength (should be unchanged):")
                test_result2 = eff.modify_stat(10.0, player, 'strength')
                print(f"    Direct call result: {test_result2}")

if __name__ == "__main__":
    try:
        test_combo_intelligence_buff()
        print("\n=== Combo Test Complete ===")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
