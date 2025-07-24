#!/usr/bin/env python3
"""
Test other character templates
"""
from game_sys.character.character_factory import create_character

# Check warrior template - has grade: 4, rarity: "COMMON"
warrior = create_character('warrior')
print(f"Warrior - Grade: {warrior.grade} ({getattr(warrior, 'grade_name', 'NONE')}), Rarity: {warrior.rarity}")

# Check dragon template - has grade: 5, rarity: "DIVINE"
dragon = create_character('dragon')
print(f"Dragon - Grade: {dragon.grade} ({getattr(dragon, 'grade_name', 'NONE')}), Rarity: {dragon.rarity}")

print("\nExpected:")
print("- Warrior: Grade 0-3 (ONE-FOUR), Rarity COMMON only")
print("- Dragon: Grade 0-4 (ONE-FIVE), Rarity COMMON-DIVINE")
