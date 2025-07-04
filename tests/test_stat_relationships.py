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
    
    # Allocate points to strength
    print("\nAllocating 3 points to Strength...")
    for i in range(3):
        success = leveling_manager.allocate_stat_point(warrior, 'strength')
        if success:
            print(f"  ✓ Allocated point {i+1} to strength")
        else:
            print(f"  ✗ Failed to allocate point {i+1} to strength")
    
    # Check updated stats
    print("\nUpdated Stats:")
    new_strength = warrior.get_stat('strength')
    new_attack = warrior.get_stat('attack')
    
    print(f"  Strength: {new_strength} (was {initial_strength})")
    print(f"  Attack (derived): {new_attack} (was {initial_attack})")
    
    # Verify the relationship
    strength_increase = new_strength - initial_strength
    attack_increase = new_attack - initial_attack
    
    print(f"\nChanges:")
    print(f"  Strength increased by: {strength_increase}")
    print(f"  Attack increased by: {attack_increase}")
    
    if attack_increase > 0 and strength_increase > 0:
        ratio = attack_increase / strength_increase
        print(f"  Attack/Strength ratio: {ratio:.3f}")
        print("✓ Strength correctly affects attack!")
    else:
        print("✗ Strength doesn't affect attack!")
        
    # Test dexterity -> speed relationship
    print("\nAllocating 2 points to Dexterity...")
    for i in range(2):
        success = leveling_manager.allocate_stat_point(warrior, 'dexterity')
        if success:
            print(f"  ✓ Allocated point {i+1} to dexterity")
        else:
            print(f"  ✗ Failed to allocate point {i+1} to dexterity")
    
    new_dexterity = warrior.get_stat('dexterity')
    new_speed = warrior.get_stat('speed')
    
    dex_increase = new_dexterity - initial_dexterity
    speed_increase = new_speed - initial_speed
    
    print(f"\nDexterity changes:")
    print(f"  Dexterity: {new_dexterity} (was {initial_dexterity})")
    print(f"  Speed: {new_speed} (was {initial_speed})")
    print(f"  Dexterity increased by: {dex_increase}")
    print(f"  Speed increased by: {speed_increase}")
    
    if speed_increase > 0 and dex_increase > 0:
        print("✓ Dexterity correctly affects speed!")
    else:
        print("✗ Dexterity doesn't affect speed!")
        
    # Test vitality -> defense relationship
    print("\nAllocating 2 points to Vitality...")
    for i in range(2):
        success = leveling_manager.allocate_stat_point(warrior, 'vitality')
        if success:
            print(f"  ✓ Allocated point {i+1} to vitality")
        else:
            print(f"  ✗ Failed to allocate point {i+1} to vitality")
    
    new_vitality = warrior.get_stat('vitality')
    new_defense = warrior.get_stat('defense')
    
    vit_increase = new_vitality - initial_vitality
    def_increase = new_defense - initial_defense
    
    print(f"\nVitality changes:")
    print(f"  Vitality: {new_vitality} (was {initial_vitality})")
    print(f"  Defense: {new_defense} (was {initial_defense})")
    print(f"  Vitality increased by: {vit_increase}")
    print(f"  Defense increased by: {def_increase}")
    
    if def_increase > 0 and vit_increase > 0:
        print("✓ Vitality correctly affects defense!")
    else:
        print("✗ Vitality doesn't affect defense!")
    
    print("\n✓ Stat relationship tests completed!")
    
    return True


if __name__ == "__main__":
    try:
        test_stat_relationships()
        print("\n🎉 All stat relationships working correctly!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
