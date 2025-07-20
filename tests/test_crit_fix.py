#!/usr/bin/env python3
"""
Quick test to verify the critical chance fix is working correctly.
"""

from game_sys.character.character_factory import create_character

def test_critical_chance():
    """Test that critical chance calculation is working properly."""
    print("=== Critical Chance Fix Test ===")
    
    # Create a dragon to test critical chance
    dragon = create_character("dragon", level=1, grade=0, rarity="COMMON")
    
    print(f"Dragon: {dragon.name}")
    print(f"Base dexterity: {dragon.base_stats.get('dexterity', 0)}")
    
    # Get the calculated critical chance
    crit_chance = dragon.get_stat('critical_chance')
    print(f"Calculated critical chance: {crit_chance:.6f} ({crit_chance:.2%})")
    
    # Expected calculation:
    # Dexterity: 26 (appears to include stat boosts)
    # Critical chance multiplier from config: 0.005
    # Expected: 26 * 0.005 = 0.13 (13.0%)
    expected = 26 * 0.005
    print(f"Expected critical chance: {expected:.6f} ({expected:.2%})")
    
    # Check if they match (allowing for small floating point differences)
    if abs(crit_chance - expected) < 0.000001:
        print("✅ Critical chance calculation is correct!")
    else:
        print("❌ Critical chance calculation is wrong!")
        print(f"   Difference: {crit_chance - expected:.6f}")
    
    # Test with higher level/grade dragon
    print("\n--- Testing with higher level dragon ---")
    high_dragon = create_character("dragon", level=50, grade=5, rarity="DIVINE")
    high_crit = high_dragon.get_stat('critical_chance')
    print(f"High level dragon critical chance: {high_crit:.6f} ({high_crit:.2%})")
    
    # This should be much higher due to grade/rarity multipliers
    if high_crit > crit_chance:
        print("✅ Grade/rarity multipliers are working!")
    else:
        print("❌ Grade/rarity multipliers might not be working correctly")

if __name__ == "__main__":
    test_critical_chance()
