#!/usr/bin/env python3
"""
Extended test to verify grade and rarity distribution
"""
from game_sys.character.character_factory import create_character
from collections import Counter

print("Testing grade and rarity distribution for 'hero' template:")
print("Template: grade=3 (max), rarity='RARE' (max)")
print("=" * 60)

# Create many characters to see distribution
grades = []
rarities = []

for i in range(50):
    hero = create_character('hero')
    grades.append(f"{hero.grade} ({getattr(hero, 'grade_name', 'NONE')})")
    rarities.append(hero.rarity)

print("Grade Distribution (50 heroes):")
grade_counts = Counter(grades)
for grade, count in sorted(grade_counts.items()):
    print(f"  {grade}: {count}")

print("\nRarity Distribution (50 heroes):")
rarity_counts = Counter(rarities)
for rarity, count in sorted(rarity_counts.items()):
    print(f"  {rarity}: {count}")

print("\n✅ Expected: Grades 0-2 (ONE-THREE), Rarities COMMON-RARE")
print("✅ No grade 3 (FOUR) or rarities beyond RARE should appear")
