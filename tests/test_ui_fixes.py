#!/usr/bin/env python3
"""
Quick test script to add Ring of Power to player inventory
Run this after starting the demo to test the UI fixes.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath('.')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory

def test_ui_ring_display():
    """Test the ring display fixes in the UI"""
    
    # Create a fresh player for testing
    player = create_character('hero')
    
    # Create Ring of Power
    ring = ItemFactory.create('ring_of_power')
    
    # Add to inventory without auto-equip
    player.inventory.add_item(ring, auto_equip=False)
    
    print("=== RING UI TEST SETUP ===")
    print(f"Player: {player.name}")
    print(f"Ring created: {ring.name}")
    print(f"Ring stats: {ring.stats}")
    print(f"Ring slot: {ring.slot}")
    print(f"Ring UUID: {ring.uuid}")
    
    print("\n=== STATS BEFORE RING ===")
    intel_before = player.get_stat('intelligence')
    wisdom_before = player.get_stat('wisdom')
    magic_before = player.get_stat('magic_power')
    print(f"Intelligence: {intel_before}")
    print(f"Wisdom: {wisdom_before}")
    print(f"Magic Power: {magic_before}")
    
    # Equip the ring
    result = player.equip_item_by_uuid(ring.uuid)
    print(f"\n=== RING EQUIP RESULT ===")
    print(f"Equip successful: {result}")
    print(f"Equipped ring: {getattr(player, 'equipped_ring', None)}")
    
    print("\n=== STATS AFTER RING ===")
    intel_after = player.get_stat('intelligence')
    wisdom_after = player.get_stat('wisdom')
    magic_after = player.get_stat('magic_power')
    print(f"Intelligence: {intel_after} (change: {intel_after - intel_before:+.1f})")
    print(f"Wisdom: {wisdom_after} (change: {wisdom_after - wisdom_before:+.1f})")
    print(f"Magic Power: {magic_after} (change: {magic_after - magic_before:+.1f})")
    
    print("\n=== INSTRUCTIONS ===")
    print("1. Go to the Character Stats tab and check if the ring appears in equipment details")
    print("2. Go to the Inventory tab and verify the ring is not in the unequipped items list")
    print("3. Check if the stats shown match the calculated values above")
    print("4. Try right-clicking on the Ring equipment slot to test context menu")
    print("5. Try unequipping using the 'Unequip Ring' button in inventory tab")
    
    # Export player for demo to access (this won't work for running demo, but useful for debugging)
    return player, ring

if __name__ == "__main__":
    test_ui_ring_display()
