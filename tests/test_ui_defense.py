#!/usr/bin/env python3
"""Quick test to verify defense updates in real-time."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game_sys.character.character_factory import create_character
from game_sys.items.item_loader import load_item


def test_ui_defense_updates():
    """Test that defense updates are reflected properly."""
    print("=== Testing UI Defense Updates ===")
    
    # Create a test character  
    character = create_character(template_id="hero")
    
    def show_defense_info():
        return (
            f"Base defense: {character.base_stats.get('defense', 0):.1f}, "
            f"Computed defense: {character.get_stat('defense'):.1f}"
        )
    
    print(f"Initial: {show_defense_info()}")
    
    # Simulate what the demo does
    armor = load_item("leather_armor")
    print(f"Equipping {armor.name}...")
    
    # Add to inventory first (like demo does)
    character.inventory.add_item(armor)
    
    # Remove from inventory and equip (like demo does)
    character.inventory.remove_item(armor)
    success = character.equip_armor(armor)
    
    print(f"After equipping: {show_defense_info()}")
    
    # Test unequipping
    unequipped = character.unequip_armor("body")
    print(f"After unequipping: {show_defense_info()}")
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    test_ui_defense_updates()
