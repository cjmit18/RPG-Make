#!/usr/bin/env python3

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath('.')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging before importing anything else
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)8s] %(name)s:%(lineno)d | %(message)s')

from game_sys.character.character_factory import create_character
from game_sys.items.factory import ItemFactory

def test_ring_equipping_from_scratch():
    print("=== Ring Equipping From Scratch ===")
    
    # Create a player
    player = create_character('hero')
    
    # Manually unequip any existing ring first (to test fresh equipping)
    if hasattr(player, 'equipped_ring') and player.equipped_ring:
        print(f"Player already has ring: {player.equipped_ring.name}")
        old_ring = player.equipped_ring
        setattr(player, 'equipped_ring', None)
        player.inventory.add_item(old_ring, auto_equip=False)
        print("Removed existing ring")
    
    # Create Ring of Power fresh
    ring_item = ItemFactory.create('ring_of_power')
    print(f"Created fresh Ring of Power: {ring_item.name}")
    
    # Test that slot is empty
    print(f"Ring slot empty: {getattr(player, 'equipped_ring', None) is None}")
    
    # Add to inventory WITHOUT auto-equip
    player.inventory.add_item(ring_item, auto_equip=False)
    print(f"Added ring to inventory (no auto-equip)")
    
    # Now test Actor.equip_item_by_uuid
    print(f"\n--- Testing Actor.equip_item_by_uuid ---")
    result = player.equip_item_by_uuid(ring_item.uuid)
    print(f"Equip result: {result}")
    print(f"Ring after equip: {getattr(player, 'equipped_ring', 'NO RING')}")
    if hasattr(player, 'equipped_ring') and player.equipped_ring:
        print(f"Equipped ring name: {player.equipped_ring.name}")
    print(f"Ring in inventory: {ring_item in player.inventory.items}")
    
    print("\n=== SUCCESS! Ring equipping is working! ===")

if __name__ == "__main__":
    test_ring_equipping_from_scratch()
