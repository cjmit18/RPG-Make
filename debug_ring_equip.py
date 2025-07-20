#!/usr/bin/env python3
"""Test script with detailed logging for ring equipping."""

from demo import SimpleGameDemo
import logging

# Set up debug logging
logging.basicConfig(level=logging.DEBUG)

# Create demo and set up game state
demo = SimpleGameDemo()
demo.setup_game_state()

# Add Ring of Power to inventory
print("Adding Ring of Power to inventory...")
from game_sys.items.item_loader import load_item
ring = load_item("ring_of_power")

if ring:
    demo.player.inventory.add_item(ring, auto_equip=False)
    print(f"Added {ring.name} to inventory")
    print(f"Ring slot: {getattr(ring, 'slot', 'no slot')}")
    print(f"Ring UUID: {getattr(ring, 'uuid', 'no UUID')}")
    
    # Check player attributes
    print(f"\nPlayer has ring attribute: {hasattr(demo.player, 'ring')}")
    print(f"Current ring: {getattr(demo.player, 'ring', 'MISSING')}")
    
    # Test direct attribute assignment first
    print("\nTesting direct attribute assignment...")
    try:
        setattr(demo.player, 'ring', ring)
        print(f"Direct assignment successful: {demo.player.ring.name}")
        setattr(demo.player, 'ring', None)  # Reset
    except Exception as e:
        print(f"Direct assignment failed: {e}")
    
    # Try using the equipment manager with detailed error handling
    print("\nTesting equipment manager...")
    from game_sys.managers.equipment_manager import equipment_manager
    
    # Test slot availability first
    try:
        available, conflict_msg = equipment_manager.check_equipment_slot_availability(demo.player, ring, 'ring')
        print(f"Slot availability: {available}, conflict: {conflict_msg}")
    except Exception as e:
        print(f"Slot availability check failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Try the actual equip operation with debug
    try:
        # Enable debug logging
        eq_logger = logging.getLogger('game_sys.managers.equipment_manager')
        eq_logger.setLevel(logging.DEBUG)
        
        success, message = equipment_manager.equip_item_with_smart_logic(demo.player, ring)
        print(f"Equipment manager result: success={success}, message={message}")
        print(f"Final equipped ring: {getattr(demo.player, 'ring', 'MISSING')}")
        
    except Exception as e:
        print(f"Equipment manager failed: {e}")
        import traceback
        traceback.print_exc()

else:
    print("Failed to load Ring of Power!")
