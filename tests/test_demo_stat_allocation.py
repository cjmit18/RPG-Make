# test_demo_stat_allocation.py
"""Test the demo's stat allocation functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from demo import SimpleGameDemo


def test_demo_manually():
    """Launch the demo for manual testing of stat allocation."""
    print("=== Manual Demo Test ===")
    print("This will launch the demo UI. Please test:")
    print("1. Go to the Leveling tab")
    print("2. Click 'Gain XP (Test)' to get stat points")
    print("3. Allocate points to different stats")
    print("4. Check the Character Stats tab to see updated values")
    print("5. Verify that attack increases with strength")
    print("6. Verify that speed increases with dexterity")
    print("7. Verify that defense increases with vitality")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
        
        # Create and run the demo
        demo = SimpleGameDemo()
        demo.run()
        
    except KeyboardInterrupt:
        print("\nDemo test cancelled.")
        return False
    except Exception as e:
        print(f"\nDemo test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("Manual demo test completed.")
    return True


def test_demo_stat_system():
    """Test the demo's stat system programmatically."""
    print("=== Programmatic Demo Test ===")
    
    try:
        # Create the demo (but don't run the UI)
        demo = SimpleGameDemo()
        
        if not hasattr(demo, 'player') or not demo.player:
            print("✗ No player created")
            return False
        
        player = demo.player
        print(f"✓ Player created: {player.name}")
        
        # Check initial stats
        initial_strength = player.get_stat('strength')
        initial_attack = player.get_stat('attack')
        print(f"Initial strength: {initial_strength}")
        print(f"Initial attack: {initial_attack}")
        
        # Set up stat points
        player.level = 3  # Should give 10 stat points
        
        # Test stat allocation
        try:
            from game_sys.character.leveling_manager import leveling_manager
            
            # Allocate 2 points to strength
            success1 = leveling_manager.allocate_stat_point(player, 'strength')
            success2 = leveling_manager.allocate_stat_point(player, 'strength')
            
            if success1 and success2:
                print("✓ Successfully allocated 2 points to strength")
                
                # Force stat update (like the demo does)
                if hasattr(player, 'update_stats'):
                    player.update_stats()
                
                # Check updated stats
                new_strength = player.get_stat('strength')
                new_attack = player.get_stat('attack')
                
                print(f"New strength: {new_strength}")
                print(f"New attack: {new_attack}")
                
                strength_increase = new_strength - initial_strength
                attack_increase = new_attack - initial_attack
                
                print(f"Strength increased by: {strength_increase}")
                print(f"Attack increased by: {attack_increase}")
                
                if attack_increase > 0 and strength_increase > 0:
                    print("✓ Stat allocation affects derived stats correctly!")
                    return True
                else:
                    print("✗ Stat allocation doesn't affect derived stats")
                    return False
            else:
                print("✗ Failed to allocate stat points")
                return False
                
        except Exception as e:
            print(f"✗ Error testing stat allocation: {e}")
            return False
        
    except Exception as e:
        print(f"✗ Error creating demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing Demo Stat Allocation System")
    print("=" * 40)
    
    # Test programmatically first
    success = test_demo_stat_system()
    
    if success:
        print("\n🎉 Programmatic test passed!")
        
        # Ask if user wants to test manually
        try:
            response = input("\nWould you like to test the UI manually? (y/n): ")
            if response.lower().startswith('y'):
                test_demo_manually()
        except KeyboardInterrupt:
            print("\nSkipping manual test.")
    else:
        print("\n❌ Programmatic test failed!")
        print("Not running manual test due to system errors.")
