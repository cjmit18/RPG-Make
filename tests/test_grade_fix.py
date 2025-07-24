#!/usr/bin/env python3
"""
Test script to demonstrate the grade and rarity issues
"""
from game_sys.character.character_factory import create_character

print("Testing character creation with grade/rarity issues:")
print("=" * 60)

# Test creating multiple heroes to see the grade/rarity behavior
for i in range(5):
    hero = create_character('hero')
    grade_name = getattr(hero, 'grade_name', 'NONE')
    print(f"Hero {i+1}: Grade={hero.grade} ({grade_name}), Rarity={hero.rarity}")

print("\nExpected behavior:")
print("- Grade should be random between 1-3 (template has grade: 3)")
print("- Grade should display as ONE, TWO, THREE not numeric values")
print("- Rarity should be random up to RARE (template has rarity: 'RARE')")
