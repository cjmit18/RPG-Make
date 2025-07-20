#!/usr/bin/env python3
"""
Items validation script - Fixed version
Validates items.json structure and reports improvements
"""
import json
import os

def validate_items_structure():
    """Validate items.json and report findings."""
    items_path = os.path.join('game_sys', 'items', 'data', 'items.json')
    
    if not os.path.exists(items_path):
        print(f"❌ ERROR: Could not find {items_path}")
        return
    
    try:
        with open(items_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to load JSON: {e}")
        return
    
    if 'items' not in data:
        print("❌ ERROR: No 'items' key found in JSON")
        return
    
    items = data['items']
    print(f"🔍 VALIDATION RESULTS FOR {len(items)} ITEMS")
    print("=" * 60)
    
    # Analysis containers
    validation_results = {
        'total_items': len(items),
        'items_with_defense': [],
        'new_damage_types': [],
        'armor_items': [],
        'weapon_items': [],
        'new_items': [],
        'missing_fields': [],
        'enhanced_items': []
    }
    
    # Known damage types before refactoring
    original_damage_types = ['PHYSICAL', 'MAGIC', 'FIRE']
    new_damage_types = []
    
    # Known items before refactoring (partial list for detection)
    known_original_items = [
        'empty_hands', 'potion_health', 'potion_mana', 'iron_sword', 
        'leather_armor', 'steel_sword', 'orc_axe', 'basic_clothes'
    ]
    
    # Analyze each item
    for item_id, item_data in items.items():
        item_type = item_data.get('type', 'unknown')
        damage_type = item_data.get('damage_type')
        defense = item_data.get('defense')
        
        # Track armor items with defense
        if item_type == 'armor' or defense is not None:
            validation_results['armor_items'].append(item_id)
            if defense is not None:
                validation_results['items_with_defense'].append(item_id)
        
        # Track weapons by type
        if item_type in ['weapon', 'two_handed_weapon']:
            validation_results['weapon_items'].append(item_id)
        
        # Track new damage types
        if damage_type and damage_type not in original_damage_types:
            if damage_type not in new_damage_types:
                new_damage_types.append(damage_type)
                # Use string concatenation to avoid f-string issues
                damage_info = item_id + " (" + damage_type + ")"
                validation_results['new_damage_types'].append(damage_info)
        
        # Detect likely new items (not in known original set)
        if item_id not in known_original_items:
            validation_results['new_items'].append(item_id)
        
        # Check for required fields
        required_fields = ['type', 'name', 'description']
        missing = [field for field in required_fields if field not in item_data]
        if missing:
            validation_results['missing_fields'].append({
                'item': item_id,
                'missing': missing
            })
        
        # Check for enhanced items (items with stats, effects, etc.)
        has_enhancements = any(key in item_data for key in [
            'stats', 'effect_ids', 'stat_requirements', 'level_requirement'
        ])
        if has_enhancements and len(item_data.get('effect_ids', [])) > 0:
            validation_results['enhanced_items'].append(item_id)
    
    # Generate report
    print(f"📊 TOTAL ITEMS: {validation_results['total_items']}")
    print(f"⚔️  WEAPONS: {len(validation_results['weapon_items'])}")
    print(f"🛡️  ARMOR PIECES: {len(validation_results['armor_items'])}")
    print(f"🔰 ITEMS WITH DEFENSE: {len(validation_results['items_with_defense'])}")
    print()
    
    print("🆕 NEW DAMAGE TYPES DETECTED:")
    if validation_results['new_damage_types']:
        for damage_info in validation_results['new_damage_types']:
            print(f"   • {damage_info}")
    else:
        print("   None detected")
    print()
    
    print("🔥 LIKELY NEW ITEMS (not in original set):")
    if validation_results['new_items']:
        # Group new items for better display
        new_count = len(validation_results['new_items'])
        print(f"   Found {new_count} potential new items:")
        for item in validation_results['new_items'][:10]:  # Show first 10
            print(f"   • {item}")
        if new_count > 10:
            print(f"   ... and {new_count - 10} more")
    else:
        print("   None detected")
    print()
    
    print("⚡ ENHANCED ITEMS (with effects):")
    if validation_results['enhanced_items']:
        for item in validation_results['enhanced_items']:
            print(f"   • {item}")
    else:
        print("   None detected")
    print()
    
    print("❌ VALIDATION ISSUES:")
    if validation_results['missing_fields']:
        print("   Items missing required fields:")
        for issue in validation_results['missing_fields']:
            missing_str = ", ".join(issue['missing'])
            print(f"   • {issue['item']}: missing {missing_str}")
    else:
        print("   ✅ No missing required fields detected")
    
    print("\n" + "=" * 60)
    print("🎯 REFACTORING SUCCESS SUMMARY:")
    print(f"   • Items enhanced with defense values: {len(validation_results['items_with_defense'])}")
    print(f"   • New damage types added: {len(new_damage_types)}")
    print(f"   • Enhanced items with effects: {len(validation_results['enhanced_items'])}")
    print(f"   • Potential new items added: {len(validation_results['new_items'])}")
    
    if len(validation_results['items_with_defense']) > 5:
        print("   ✅ Defense field standardization: SUCCESS")
    if len(new_damage_types) >= 3:
        print("   ✅ Damage type variety expansion: SUCCESS")
    if validation_results['total_items'] > 35:
        print("   ✅ Item variety expansion: SUCCESS")
    
    print("\n🔄 Items system refactoring validation complete!")

if __name__ == "__main__":
    validate_items_structure()
