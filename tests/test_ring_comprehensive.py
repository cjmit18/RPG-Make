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

def test_ring_stats_and_display():
    print("=== Ring Stats and Display Test ===")
    
    # Create a player
    player = create_character('hero')
    print(f"Created player: {player.name}")
    
    # Check stats before ring
    print(f"\n--- BEFORE Ring ---")
    intelligence_before = player.get_stat('intelligence') if hasattr(player, 'get_stat') else player.base_stats.get('intelligence', 0)
    wisdom_before = player.get_stat('wisdom') if hasattr(player, 'get_stat') else player.base_stats.get('wisdom', 0)
    magic_power_before = player.get_stat('magic_power') if hasattr(player, 'get_stat') else 0
    
    print(f"Intelligence: {intelligence_before}")
    print(f"Wisdom: {wisdom_before}")
    print(f"Magic Power: {magic_power_before}")
    
    # Create Ring of Power and check its stats
    ring_item = ItemFactory.create('ring_of_power')
    print(f"\n--- Ring Item Details ---")
    print(f"Ring name: {ring_item.name}")
    print(f"Ring slot: {ring_item.slot}")
    print(f"Ring stats: {getattr(ring_item, 'stats', 'No stats attribute')}")
    if hasattr(ring_item, 'effect_ids'):
        print(f"Ring effects: {ring_item.effect_ids}")
    
    # Add to inventory WITHOUT auto-equip
    player.inventory.add_item(ring_item, auto_equip=False)
    print(f"Added ring to inventory (no auto-equip)")
    
    # Equip the ring using UUID method
    result = player.equip_item_by_uuid(ring_item.uuid)
    print(f"Ring equip result: {result}")
    
    # Verify it's equipped
    equipped_ring = getattr(player, 'equipped_ring', None)
    print(f"Equipped ring: {equipped_ring.name if equipped_ring else 'None'}")
    
    # Check stats after ring
    print(f"\n--- AFTER Ring ---")
    intelligence_after = player.get_stat('intelligence') if hasattr(player, 'get_stat') else player.base_stats.get('intelligence', 0)
    wisdom_after = player.get_stat('wisdom') if hasattr(player, 'get_stat') else player.base_stats.get('wisdom', 0)
    magic_power_after = player.get_stat('magic_power') if hasattr(player, 'get_stat') else 0
    
    print(f"Intelligence: {intelligence_after} (change: {intelligence_after - intelligence_before:+})")
    print(f"Wisdom: {wisdom_after} (change: {wisdom_after - wisdom_before:+})")
    print(f"Magic Power: {magic_power_after} (change: {magic_power_after - magic_power_before:+})")
    
    # Test unequip
    print(f"\n--- TESTING UNEQUIP ---")
    unequipped_item = player.unequip_item_by_slot('ring')
    print(f"Unequipped item: {unequipped_item.name if unequipped_item else 'None'}")
    print(f"Ring in inventory after unequip: {ring_item in player.inventory.items}")
    
    # Stats after unequip
    print(f"\n--- AFTER Unequip ---")
    intelligence_final = player.get_stat('intelligence') if hasattr(player, 'get_stat') else player.base_stats.get('intelligence', 0)
    wisdom_final = player.get_stat('wisdom') if hasattr(player, 'get_stat') else player.base_stats.get('wisdom', 0)
    magic_power_final = player.get_stat('magic_power') if hasattr(player, 'get_stat') else 0
    
    print(f"Intelligence: {intelligence_final} (back to: {intelligence_before}? {intelligence_final == intelligence_before})")
    print(f"Wisdom: {wisdom_final} (back to: {wisdom_before}? {wisdom_final == wisdom_before})")
    print(f"Magic Power: {magic_power_final} (back to: {magic_power_before}? {magic_power_final == magic_power_before})")
    
    print(f"\n=== RING SYSTEM TEST COMPLETE ===")

if __name__ == "__main__":
    test_ring_stats_and_display()
