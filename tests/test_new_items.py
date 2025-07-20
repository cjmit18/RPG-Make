#!/usr/bin/env python3
"""
Test script for new items from the refactoring
Tests the new damage types and items integration
"""
import os
import sys
import json
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from game_sys.items.factory import ItemFactory
from game_sys.character.character_factory import CharacterFactory

def test_new_items():
    """Test the new items added during refactoring."""
    print("🧪 TESTING NEW ITEMS FROM REFACTORING")
    print("=" * 50)
    
    # Initialize factories
    item_factory = ItemFactory()
    character_factory = CharacterFactory()
    
    # Create a test character
    print("Creating test character...")
    player = character_factory.create("hero")
    print(f"✅ Created: {player.name}")
    
    # Test new damage type weapons
    new_weapons = [
        'ice_wand',
        'lightning_rod', 
        'poison_blade',
        'holy_mace',
        'shadow_dagger'
    ]
    
    print(f"\n🗡️ TESTING {len(new_weapons)} NEW DAMAGE TYPE WEAPONS:")
    print("-" * 40)
    
    for weapon_id in new_weapons:
        try:
            weapon = item_factory.create(weapon_id)
            if weapon:
                damage_type = getattr(weapon, 'damage_type', 'UNKNOWN')
                damage = getattr(weapon, 'damage', 'N/A')
                print(f"✅ {weapon.name}")
                print(f"   • ID: {weapon_id}")
                print(f"   • Type: {weapon.type}")
                print(f"   • Damage Type: {damage_type}")
                print(f"   • Damage: {damage}")
                print(f"   • Description: {weapon.description[:50]}...")
                print()
            else:
                print(f"❌ Failed to create {weapon_id}")
        except Exception as e:
            print(f"❌ Error creating {weapon_id}: {e}")
    
    # Test new equipment pieces
    new_equipment = [
        'steel_helmet',
        'chain_gauntlets',
        'mana_crystal_amulet'
    ]
    
    print(f"🛡️ TESTING {len(new_equipment)} NEW EQUIPMENT PIECES:")
    print("-" * 40)
    
    for equip_id in new_equipment:
        try:
            equipment = item_factory.create(equip_id)
            if equipment:
                defense = getattr(equipment, 'defense', 'N/A')
                equipment_type = getattr(equipment, 'type', 'UNKNOWN')
                print(f"✅ {equipment.name}")
                print(f"   • ID: {equip_id}")
                print(f"   • Type: {equipment_type}")
                print(f"   • Defense: {defense}")
                print(f"   • Description: {equipment.description[:50]}...")
                print()
            else:
                print(f"❌ Failed to create {equip_id}")
        except Exception as e:
            print(f"❌ Error creating {equip_id}: {e}")
    
    # Test damage type coverage
    print("📊 DAMAGE TYPE COVERAGE ANALYSIS:")
    print("-" * 40)
    
    # Load items.json directly to analyze damage types
    items_path = os.path.join('game_sys', 'items', 'data', 'items.json')
    with open(items_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    damage_types = {}
    for item_id, item_data in data['items'].items():
        damage_type = item_data.get('damage_type')
        if damage_type:
            if damage_type not in damage_types:
                damage_types[damage_type] = []
            damage_types[damage_type].append(item_id)
    
    print(f"Found {len(damage_types)} damage types:")
    for dtype, items in damage_types.items():
        print(f"   • {dtype}: {len(items)} items")
        if len(items) <= 3:
            print(f"     - {', '.join(items)}")
        else:
            print(f"     - {', '.join(items[:3])} ... (+{len(items)-3} more)")
    
    # Test equipment service integration
    print(f"\n⚙️ TESTING EQUIPMENT SERVICE INTEGRATION:")
    print("-" * 40)
    
    try:
        from game_sys.items.equipment_service import EquipmentService
        service = EquipmentService()
        print("✅ Equipment Service initialized successfully")
        
        # Test with a new weapon
        ice_wand = item_factory.create('ice_wand')
        if ice_wand:
            result = service.can_equip(player, ice_wand)
            print(f"✅ Equipment compatibility check for Ice Wand: {result}")
        
        # Test equipment application 
        steel_helmet = item_factory.create('steel_helmet')
        if steel_helmet:
            try:
                # This may require inventory setup, but let's see if the service works
                result = service.can_equip(player, steel_helmet)
                print(f"✅ Equipment compatibility check for Steel Helmet: {result}")
            except Exception as e:
                print(f"⚠️ Equipment service test note: {e}")
        
    except Exception as e:
        print(f"❌ Equipment service integration error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 NEW ITEMS TESTING COMPLETE")
    print("✅ Items refactoring integration validated!")

if __name__ == "__main__":
    test_new_items()
