#!/usr/bin/env python3
"""Test armor equipping and defense stat updates."""

import sys
import os
from game_sys.character.character_factory import create_character
from game_sys.items.item_loader import load_item

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_armor_equipping():
    """Test that equipping armor properly updates defense stats."""
    print("=== Testing Armor Equipping ===")
    
    # Create a test character
    character = create_character(template_id="hero")
    
    print(f"Character: {character.name}")
    print(f"Initial vitality: {character.base_stats.get('vitality', 0):.1f}")
    print(f"Initial defense base stat: {character.base_stats.get('defense', 0):.1f}")
    print(f"Initial computed defense: {character.get_stat('defense'):.1f}")
    
    # Check equipped clothing
    current_body = getattr(character, 'equipped_body', None)
    if current_body:
        print(f"Currently equipped body armor: {current_body.name}")
        print(f"  Stats: {getattr(current_body, 'stats', {})}")
    
    # Get an armor item
    armor = load_item("leather_armor")
    
    if armor:
        print(f"\nArmor to equip: {armor.name}")
        print(f"Armor stats: {getattr(armor, 'stats', {})}")
        
        # Equip the armor
        success = character.equip_armor(armor)
        print(f"Equip successful: {success}")
        
        if success:
            print(f"Vitality after equipping: {character.base_stats.get('vitality', 0):.1f}")
            print(f"Defense base stat after equipping: {character.base_stats.get('defense', 0):.1f}")
            print(f"Computed defense after equipping: {character.get_stat('defense'):.1f}")
            
            # Check what's equipped now
            new_body = getattr(character, 'equipped_body', None)
            if new_body:
                print(f"Now equipped body armor: {new_body.name}")
                print(f"  Stats: {getattr(new_body, 'stats', {})}")
            
            # Unequip the armor
            unequipped = character.unequip_armor("body")
            unequipped_name = unequipped.name if unequipped else 'None'
            print(f"\nUnequipped: {unequipped_name}")
            print(f"Vitality after unequipping: {character.base_stats.get('vitality', 0):.1f}")
            print(f"Defense base stat after unequipping: {character.base_stats.get('defense', 0):.1f}")
            print(f"Computed defense after unequipping: {character.get_stat('defense'):.1f}")
            
            # Check what's equipped now
            final_body = getattr(character, 'equipped_body', None)
            if final_body:
                print(f"Finally equipped body armor: {final_body.name}")
                print(f"  Stats: {getattr(final_body, 'stats', {})}")
            else:
                print("No body armor equipped after unequipping")
    else:
        print("Could not find leather_armor item")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_armor_equipping()
