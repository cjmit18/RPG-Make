#!/usr/bin/env python3
"""Test script to check ring equipping functionality."""

from demo import SimpleGameDemo

# Create demo and set up game state
demo = SimpleGameDemo()
demo.setup_game_state()

print("Player inventory:")
items = demo.player.inventory.list_items()
for item in items:
    slot = getattr(item, 'slot', 'no slot')
    print(f"- {item.name} ({slot})")

print("\nLooking for Ring of Power...")
ring_items = [item for item in items if 'Ring of Power' in item.name]

if ring_items:
    ring = ring_items[0]
    print(f"Found: {ring.name}")
    print(f"Ring slot: {getattr(ring, 'slot', 'no slot')}")
    
    print("\nTrying to equip Ring of Power...")
    try:
        # Check if ring attribute exists
        print(f"ring attribute before: {hasattr(demo.player, 'ring')}")
        print(f"Current ring value: {getattr(demo.player, 'ring', 'NOT FOUND')}")
        
        # Try to equip using equipment manager
        from game_sys.managers.equipment_manager import equipment_manager
        success, message = equipment_manager.equip_item_with_smart_logic(demo.player, ring)
        print(f"Equip result: {success}")
        print(f"Equip message: {message}")
        
        # Check after equipping
        print(f"ring attribute after: {hasattr(demo.player, 'ring')}")
        print(f"Final ring value: {getattr(demo.player, 'ring', 'NOT FOUND')}")
        
        if hasattr(demo.player, 'ring') and demo.player.ring:
            ring = demo.player.ring
            print(f"Successfully equipped: {ring.name}")
        else:
            print("Ring not equipped - checking why...")
            
    except Exception as e:
        print(f"Error during equipping: {e}")
        import traceback
        traceback.print_exc()
        
else:
    print("Ring of Power not found in inventory!")
    
    # Let's add it manually for testing
    print("Adding Ring of Power to inventory...")
    from game_sys.items.item_loader import load_item
    try:
        ring = load_item("ring_of_power")
        if ring:
            demo.player.inventory.add_item(ring, auto_equip=False)
            print(f"Added {ring.name} to inventory")
            
            # Try equipping now using equipment manager
            from game_sys.managers.equipment_manager import equipment_manager
            success, message = equipment_manager.equip_item_with_smart_logic(demo.player, ring)
            print(f"Equip result: {success}")
            print(f"Equip message: {message}")
            print(f"Equipped ring: {getattr(demo.player, 'ring', 'NOT FOUND')}")
        else:
            print("Failed to load ring_of_power item")
    except Exception as e:
        print(f"Error adding ring: {e}")
        import traceback
        traceback.print_exc()
