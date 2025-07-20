#!/usr/bin/env python3
"""Test script to verify expanded stats display in character and leveling screens."""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test the demo with expanded stats
print("=== Testing Expanded Stats Display ===")
print("This test will start the demo to verify that character and leveling screens show all stats.")
print("1. Check Character Stats tab - should show comprehensive stats in categories")
print("2. Check Leveling tab - should show expanded stats with all categories")
print("3. Create and equip a Ring of Power to test stat bonuses display")
print()

try:
    from demo import SimpleGameDemo
    
    print("Starting demo with expanded stats...")
    demo = SimpleGameDemo()
    
    # Test that the player has comprehensive stats
    if hasattr(demo, 'player') and demo.player:
        print("\nPlayer stats available:")
        
        # Test base_stats
        if hasattr(demo.player, 'base_stats'):
            print(f"  Base stats count: {len(demo.player.base_stats)}")
            print(f"  Base stats: {list(demo.player.base_stats.keys())[:10]}...")  # Show first 10
        
        # Test get_stat method
        if hasattr(demo.player, 'get_stat'):
            print("  get_stat method available")
            # Test a few stats
            for stat in ['strength', 'intelligence', 'max_health', 'critical_chance']:
                try:
                    value = demo.player.get_stat(stat)
                    print(f"    {stat}: {value}")
                except Exception as e:
                    print(f"    {stat}: Error - {e}")
        
        print(f"\nPlayer level: {getattr(demo.player, 'level', 'Unknown')}")
        print(f"Player name: {getattr(demo.player, 'name', 'Unknown')}")
    
    print("\n=== Demo Instructions ===")
    print("1. Go to 'Character Stats' tab to see expanded stats display")
    print("2. Go to 'Leveling' tab to see comprehensive stats in organized categories")
    print("3. Go to 'Inventory' tab, create a 'ring_of_power', equip it, then check stats again")
    print("4. Stats should now show equipment bonuses and effective values")
    print()
    print("Starting demo window...")
    
    demo.run()
    
except Exception as e:
    print(f"Error running demo: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
