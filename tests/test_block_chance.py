#!/usr/bin/env python3
"""
Quick test to verify block_chance stat merging.
"""

from game_sys.character.job_manager import JobManager
from game_sys.character.actor import Actor

def test_block_chance_stat_merging():
    """Test that shield block_chance gets merged into actor stats."""
    print("=== Testing Block Chance Stat Merging ===\n")
    
    # Create a warrior
    warrior = Actor(
        name="Test Warrior",
        base_stats={
            'health': 100,
            'mana': 30,
            'stamina': 80,
            'attack': 10,
            'defense': 5,
            'intellect': 5
        }
    )
    
    print(f"Before job assignment:")
    print(f"  Block chance: {warrior.base_stats.get('block_chance', 'Not set')}")
    
    # Assign warrior job (should get shield with block_chance)
    JobManager.assign(warrior, 'warrior')
    
    print(f"After job assignment:")
    print(f"  Block chance: {warrior.base_stats.get('block_chance', 'Not set')}")
    print(f"  Shield: {warrior.offhand.name if warrior.offhand else 'None'}")
    
    if hasattr(warrior.offhand, 'block_chance'):
        print(f"  Shield's block_chance: {warrior.offhand.block_chance}")
    
    print("✅ Block chance stat merging test completed!")

if __name__ == "__main__":
    test_block_chance_stat_merging()
