#!/usr/bin/env python3
"""
Test script for the updated loot system.
This tests that the loot system correctly uses the grades and rarities
defined in the configuration system.
"""

import sys
import os
from pprint import pprint

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import after path adjustment
from game_sys.loot.loot_table import LootTable


def main():
    """Test the loot system"""
    print("\n=== LOOT SYSTEM TEST ===\n")
    
    # Create instances
    loot_table = LootTable()
    
    # Test configuration values
    print("Grades from config:", loot_table.grades)
    print("Rarities from config:", loot_table.rarities)
    print("\nGrade weights:")
    if loot_table.grade_weights:
        for grade, weight in loot_table.grade_weights.items():
            print(f"  {grade}: {weight:.2f}")
    else:
        print("  No grade weights available")
    print("\nRarity weights:")
    if loot_table.base_drop_rates:
        for rarity, weight in loot_table.base_drop_rates.items():
            print(f"  {rarity}: {weight:.3f}")
    else:
        print("  No rarity weights available")
    
    # Test loot generation for different enemy types
    enemy_types = ["dragon", "orc", "goblin", "unknown_enemy"]
    player_luck = 15  # Higher luck for better drops
    
    print("\n=== ENEMY LOOT TABLES ===\n")
    
    for enemy_type in enemy_types:
        print(f"\nTesting loot for: {enemy_type}")
        
        # Get loot table
        table = loot_table.get_enemy_loot_table(enemy_type)
        print(f"Loot table found: {'Yes' if table else 'No, using default'}")
        
        # Test grade determination
        grades = {}
        for _ in range(100):
            grade = loot_table.determine_item_grade(enemy_type, player_luck)
            grades[grade] = grades.get(grade, 0) + 1
        
        print("\nGrade distribution (100 rolls):")
        pprint(grades)
        
        # Test rarity determination
        rarities = {}
        for _ in range(100):
            rarity = loot_table.determine_item_rarity(enemy_type, player_luck)
            rarities[rarity] = rarities.get(rarity, 0) + 1
        
        print("\nRarity distribution (100 rolls):")
        pprint(rarities)
        
        # Test possible items
        possible_items = loot_table.get_possible_items(enemy_type)
        print(f"\nPossible items ({len(possible_items)}):")
        print(", ".join(possible_items) if possible_items else "None")
        
        # Test level determination
        levels = {}
        for _ in range(10):
            level = loot_table.determine_item_level(
                enemy_level=10,  # Standard enemy level
                enemy_type=enemy_type
            )
            levels[level] = levels.get(level, 0) + 1
        
        print("\nItem level distribution (10 rolls):")
        pprint(levels)
        
        print("-" * 50)
    
    print("\n=== TEST COMPLETE ===\n")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
