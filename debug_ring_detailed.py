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
from game_sys.managers.equipment_manager import EquipmentManager

def test_ring_equipping():
    print("=== Ring Equipping Debug Test ===")
    
    # Create a player
    player = create_character('hero')
    equipment_manager = EquipmentManager()
    
    # Create Ring of Power
    ring_item = ItemFactory.create('ring_of_power')
    player.inventory.add_item(ring_item)
    print(f"Added Ring of Power to inventory")
    
    # Check initial state
    print(f"\n--- Initial State ---")
    print(f"Ring slot: {ring_item.slot}")
    print(f"Ring UUID: {ring_item.uuid}")
    print(f"Player has ring attribute: {hasattr(player, 'equipped_ring')}")
    print(f"Current ring: {getattr(player, 'equipped_ring', 'MISSING ATTRIBUTE')}")
    print(f"Player has equipment dict: {hasattr(player, 'equipment')}")
    if hasattr(player, 'equipment'):
        print(f"Equipment dict keys: {list(player.equipment.keys())}")
        print(f"Ring in equipment: {'ring' in player.equipment}")
        if 'ring' in player.equipment:
            print(f"Equipment ring value: {player.equipment.get('ring')}")
    
    # Test equipping via Actor.equip_item_by_uuid
    print(f"\n--- Testing Actor.equip_item_by_uuid ---")
    try:
        result = player.equip_item_by_uuid(ring_item.uuid)
        print(f"Actor equip result: {result}")
    except Exception as e:
        print(f"Actor equip error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check state after equip attempt
    print(f"\n--- After Actor Equip ---")
    print(f"Current ring: {getattr(player, 'equipped_ring', 'MISSING ATTRIBUTE')}")
    if hasattr(player, 'equipment'):
        print(f"Ring in equipment dict: {player.equipment.get('ring')}")
    print(f"Item in inventory: {ring_item in player.inventory.items}")
    
    # Test equipment manager
    print(f"\n--- Testing Equipment Manager ---")
    # Add back to inventory if removed
    if ring_item not in player.inventory.items:
        player.inventory.add_item(ring_item)
    
    result = equipment_manager.equip_item(player, ring_item)
    print(f"Equipment manager result: success={result.success}, message={result.message}")
    
    # Final check
    print(f"\n--- Final State ---")
    print(f"Final ring via attribute: {getattr(player, 'equipped_ring', 'MISSING ATTRIBUTE')}")
    if hasattr(player, 'equipment'):
        print(f"Final ring via dict: {player.equipment.get('ring')}")
    print(f"Ring in inventory: {ring_item in player.inventory.items}")
    
    # Test getting equipment directly
    print(f"\n--- Direct Equipment Check ---")
    try:
        if hasattr(player, 'equipped_ring'):
            direct_ring = player.equipped_ring
            print(f"Direct attribute access: {direct_ring}")
            if direct_ring:
                print(f"Direct ring type: {type(direct_ring)}")
                print(f"Direct ring name: {getattr(direct_ring, 'name', 'NO NAME')}")
    except Exception as e:
        print(f"Direct access error: {e}")

if __name__ == "__main__":
    test_ring_equipping()
