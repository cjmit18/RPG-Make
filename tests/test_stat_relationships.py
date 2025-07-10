# test_stat_relationships.py
"""Test that traditional RPG stats properly affect derived stats like attack."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_sys.character.character_factory import create_character
from game_sys.character.leveling_manager import leveling_manager


def test_stat_relationships():
    """Test that allocating traditional RPG stats affects derived stats."""
    print("=== Testing Stat Relationships ===")
    
    # Create a warrior character
    warrior = create_character("warrior")
    print(f"Created: {warrior.name}")
    
    # Check initial stats
    print("\nInitial Stats:")
    initial_strength = warrior.get_stat('strength')
    initial_attack = warrior.get_stat('attack')
    initial_dexterity = warrior.get_stat('dexterity')
    initial_speed = warrior.get_stat('speed')
    initial_vitality = warrior.get_stat('vitality')
    initial_defense = warrior.get_stat('defense')
    
    print(f"  Strength: {initial_strength}")
    print(f"  Attack (derived): {initial_attack}")
    print(f"  Dexterity: {initial_dexterity}")
    print(f"  Speed (derived): {initial_speed}")
    print(f"  Vitality: {initial_vitality}")
    print(f"  Defense (derived): {initial_defense}")
    
    # Set up the character to have stat points available
    warrior.level = 3  # Level 3 should give 10 stat points
    
    # Test 1: Strength -> Attack relationship
    print("\nAllocating 3 points to Strength...")
    for i in range(3):
        success = leveling_manager.allocate_stat_point(warrior, 'strength')
        assert success, f"Failed to allocate point {i+1} to strength"
        print(f"  ✓ Allocated point {i+1} to strength")
    
    new_strength = warrior.get_stat('strength')
    new_attack = warrior.get_stat('attack')
    
    strength_increase = new_strength - initial_strength
    attack_increase = new_attack - initial_attack
    
    print(f"\nChanges:")
    print(f"  Strength increased by: {strength_increase}")
    print(f"  Attack increased by: {attack_increase}")
    
    assert strength_increase == 3, f"Expected strength to increase by 3, got {strength_increase}"
    assert attack_increase > 0, "Attack should increase when strength increases"
    ratio = attack_increase / strength_increase
    assert 1.8 <= ratio <= 2.2, f"Attack/Strength ratio ({ratio:.3f}) should be ~2.0"
    print(f"  Attack/Strength ratio: {ratio:.3f}")
    
    # Test 2: Dexterity -> Speed relationship
    print("\nAllocating 2 points to Dexterity...")
    for i in range(2):
        success = leveling_manager.allocate_stat_point(warrior, 'dexterity')
        assert success, f"Failed to allocate point {i+1} to dexterity"
        print(f"  ✓ Allocated point {i+1} to dexterity")
    
    new_dexterity = warrior.get_stat('dexterity')
    new_speed = warrior.get_stat('speed')
    
    dex_increase = new_dexterity - initial_dexterity
    speed_increase = new_speed - initial_speed
    
    assert dex_increase == 2, f"Expected dexterity to increase by 2, got {dex_increase}"
    assert speed_increase > 0, "Speed should increase when dexterity increases"
    speed_ratio = speed_increase / dex_increase
    assert 0.8 <= speed_ratio <= 1.2, f"Speed/Dexterity ratio ({speed_ratio:.3f}) should be ~1.0"
    
    print(f"\nDexterity changes:")
    print(f"  Dexterity increased by: {dex_increase}")
    print(f"  Speed increased by: {speed_increase}")
    print(f"  Speed/Dexterity ratio: {speed_ratio:.3f}")
    
    # Test 3: Vitality -> Defense relationship
    print("\nAllocating 2 points to Vitality...")
    for i in range(2):
        success = leveling_manager.allocate_stat_point(warrior, 'vitality')
        assert success, f"Failed to allocate point {i+1} to vitality"
        print(f"  ✓ Allocated point {i+1} to vitality")
    
    new_vitality = warrior.get_stat('vitality')
    new_defense = warrior.get_stat('defense')
    
    vit_increase = new_vitality - initial_vitality
    def_increase = new_defense - initial_defense
    
    assert vit_increase == 2, f"Expected vitality to increase by 2, got {vit_increase}"
    assert def_increase > 0, "Defense should increase when vitality increases"
    def_ratio = def_increase / vit_increase
    assert 0.8 <= def_ratio <= 1.2, f"Defense/Vitality ratio ({def_ratio:.3f}) should be ~1.0"
    
    print(f"\nVitality changes:")
    print(f"  Vitality increased by: {vit_increase}")
    print(f"  Defense increased by: {def_increase}")
    print(f"  Defense/Vitality ratio: {def_ratio:.3f}")
    
    print("\n✓ All stat relationships verified with assertions!")
    return True


if __name__ == "__main__":
    try:
        test_stat_relationships()
        print("\n🎉 All stat relationships working correctly!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
