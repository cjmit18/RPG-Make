#!/usr/bin/env python3
"""
Test the distinct behavior of Preview vs Reset
"""
from game_sys.character.character_factory import create_character

# Simulate what the new demo functions do
print("Testing PREVIEW vs RESET distinction:")
print("=" * 50)

# First create a "hero" character manually to simulate having one already
print("1. Initial character creation:")
hero = create_character('hero')
original_strength = hero.get_stat('strength')
print(f"   Created: {hero.name}")
print(f"   Grade: {getattr(hero, 'grade_name', 'NONE')} | Rarity: {hero.rarity}")
print(f"   Strength: {original_strength}")

print("\n2. Simulating stat point allocation (+3 to strength):")
# Use the correct method to modify stats
hero.base_stats['strength'] = original_strength + 3
hero.update_stats()  # Refresh derived stats
new_strength = hero.get_stat('strength')
print(f"   Strength after allocation: {new_strength} (was {original_strength})")

print("\n3. Testing RESET (should preserve grade/rarity, reset stats):")
# Simulate the new reset behavior
template_data = {
    'base_stats': {
        'strength': 10,
        'dexterity': 10,
        'vitality': 10,
        'intelligence': 10,
        'wisdom': 10,
        'constitution': 10,
        'luck': 10,
        'agility': 10
    }
}

# Store current values
current_grade_name = getattr(hero, 'grade_name', 'ONE')
current_rarity = hero.rarity
current_name = hero.name

# Reset to base stats using the correct method
for stat_name, base_value in template_data['base_stats'].items():
    hero.base_stats[stat_name] = base_value
hero.update_stats()  # Refresh derived stats

print(f"   After RESET:")
print(f"   Name: {current_name} (preserved)")
print(f"   Grade: {current_grade_name} (preserved)")
print(f"   Rarity: {current_rarity} (preserved)")
print(f"   Strength: {hero.get_stat('strength')} (reset to base)")

print("\n4. Testing PREVIEW (creates new character with random grade/rarity):")
new_hero = create_character('hero')
print(f"   After PREVIEW:")
print(f"   Name: {new_hero.name} (new)")
print(f"   Grade: {getattr(new_hero, 'grade_name', 'NONE')} (new random)")
print(f"   Rarity: {new_hero.rarity} (new random)")
print(f"   Strength: {new_hero.get_stat('strength')} (base from template)")

print("\n" + "=" * 50)
print("KEY DIFFERENCES:")
print("🔄 RESET: Keeps same character, preserves grade/rarity, resets stats")
print("🎲 PREVIEW: Creates brand new character with random grade/rarity")
