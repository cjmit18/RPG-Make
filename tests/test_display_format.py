#!/usr/bin/env python3
"""
Test the demo character display formatting
"""
from game_sys.character.character_factory import create_character

# Test the _extract_character_stats function behavior
hero = create_character('hero')
print(f"Raw character attributes:")
print(f"  grade: {hero.grade}")
print(f"  grade_name: {getattr(hero, 'grade_name', 'NONE')}")
print(f"  rarity: {hero.rarity}")

# Test how the demo service would extract stats
try:
    # Use grade_name for display instead of numeric grade
    grade_display = getattr(hero, 'grade_name', 'UNKNOWN')
    if not grade_display or grade_display == 'UNKNOWN':
        # Fallback to numeric grade if no grade_name
        grade_display = str(getattr(hero, 'grade', 'UNKNOWN'))
    
    print(f"\nDemo display format:")
    print(f"  Grade shown in UI: {grade_display}")
    print(f"  Rarity shown in UI: {getattr(hero, 'rarity', 'COMMON')}")
    
    print(f"\n🗡️ Character: {hero.name}")
    print(f"📊 Level: {getattr(hero, 'level', 1)} | Grade: {grade_display} | Rarity: {getattr(hero, 'rarity', 'COMMON')}")
    
except Exception as e:
    print(f"Error: {e}")
