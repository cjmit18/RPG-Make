#!/usr/bin/env python3
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from game_sys.character.character_factory import create_character

# Test character creation and properties
hero = create_character('hero')
print(f"Created character: {hero.name}")
print(f"Current health: {hero.current_health}")
print(f"Health property: {hero.health}")

# Test stats property
print(f"Has stats property: {hasattr(hero, 'stats')}")
print(f"Stats effective: {hero.stats.effective()}")

# Test setting base stats
hero.stats.set_base("attack", 50)
print(f"Attack after setting: {hero.get_stat('attack')}")

print("✓ All basic properties work!")
