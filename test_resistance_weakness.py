#!/usr/bin/env python3
"""
Test Resistance/Weakness System
===============================

Quick test to verify that the resistance and weakness system is working correctly
after the combat engine fix.
"""

from game_sys.character.character_factory import create_character
from game_sys.character.character_service import create_character_with_random_stats
from game_sys.core.damage_type_utils import get_damage_type_by_name
from game_sys.combat.combat_service import CombatService

def test_resistance_weakness():
    """Test that resistances and weaknesses are working correctly."""
    print("=== Testing Resistance/Weakness System ===")
    
    # Create a dragon (has FIRE resistance and ICE weakness)
    dragon = create_character_with_random_stats("dragon")
    if not dragon:
        print("Failed to create dragon")
        return
        
    print(f"Created {dragon.name}")
    print(f"Health: {dragon.current_health}/{dragon.max_health}")
    print(f"Resistances: {dragon.resistances}")
    print(f"Weaknesses: {dragon.weaknesses}")
    
    # Test different damage types
    damage_types_to_test = [
        ("FIRE", "should be resisted"),
        ("ICE", "should be amplified (weakness)"), 
        ("PHYSICAL", "should be resisted"),
        ("LIGHTNING", "should be normal")
    ]
    
    for damage_type_name, expected in damage_types_to_test:
        print(f"\n--- Testing {damage_type_name} damage ({expected}) ---")
        
        # Reset dragon health
        dragon.current_health = dragon.max_health
        initial_hp = dragon.current_health
        
        # Get damage type
        damage_type = get_damage_type_by_name(damage_type_name)
        print(f"Using damage type: {damage_type}")
        
        # Apply 100 damage of this type
        test_damage = 100.0
        print(f"Applying {test_damage} base damage")
        
        # Test take_damage directly
        remaining_hp = dragon.take_damage(test_damage, attacker=None, damage_type=damage_type)
        actual_damage = initial_hp - dragon.current_health
        
        print(f"Actual damage dealt: {actual_damage}")
        print(f"Health: {initial_hp} -> {dragon.current_health}")
        
        # Calculate expected damage based on resistances/weaknesses
        if damage_type in dragon.resistances:
            resistance = dragon.resistances[damage_type]
            expected_damage = test_damage * (1.0 - resistance)
            print(f"Expected with {resistance:.1%} resistance: {expected_damage}")
        elif damage_type in dragon.weaknesses:
            weakness = dragon.weaknesses[damage_type]
            expected_damage = test_damage * (1.0 + weakness)
            print(f"Expected with {weakness:.1%} weakness: {expected_damage}")
        else:
            expected_damage = test_damage
            print(f"Expected (no modifier): {expected_damage}")
        
        print(f"Difference: {abs(actual_damage - expected_damage):.2f}")
        
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_resistance_weakness()
