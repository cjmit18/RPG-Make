#!/usr/bin/env python3
"""
Effect ID Validation Script
==========================

Validates all effect_ids used in items.json to ensure they're properly defined
and can be created by the EffectFactory.
"""
import json
import os
import sys
from collections import defaultdict
from typing import Set, List, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from game_sys.effects.factory import EffectFactory
from game_sys.effects.registry import EffectRegistry


def extract_all_effect_ids() -> Dict[str, List[str]]:
    """Extract all effect IDs from items.json grouped by item."""
    items_path = os.path.join('game_sys', 'items', 'data', 'items.json')
    
    if not os.path.exists(items_path):
        print(f"❌ ERROR: Could not find {items_path}")
        return {}
    
    try:
        with open(items_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to load JSON: {e}")
        return {}
    
    if 'items' not in data:
        print("❌ ERROR: No 'items' key found in JSON")
        return {}
    
    effect_ids_by_item = {}
    all_effect_ids = set()
    
    for item_id, item_data in data['items'].items():
        effect_ids = item_data.get('effect_ids', [])
        if effect_ids:
            effect_ids_by_item[item_id] = effect_ids
            all_effect_ids.update(effect_ids)
    
    print(f"📊 Found {len(all_effect_ids)} unique effect IDs across {len(effect_ids_by_item)} items")
    return effect_ids_by_item


def validate_effect_id(effect_id: str) -> tuple[bool, str, Any]:
    """
    Validate a single effect ID.
    
    Returns:
        (is_valid, error_message, effect_object_or_none)
    """
    try:
        # Try to create the effect using the factory
        effect = EffectFactory.create_from_id(effect_id)
        
        if effect is None:
            return False, "Factory returned None", None
        
        # Check if it's a NullEffect (fallback)
        if hasattr(effect, '__class__') and effect.__class__.__name__ == 'NullEffect':
            return False, "Created NullEffect (unknown effect type)", effect
        
        return True, "Valid", effect
        
    except Exception as e:
        return False, f"Exception during creation: {str(e)}", None


def categorize_effect_ids(effect_ids: Set[str]) -> Dict[str, List[str]]:
    """Categorize effect IDs by pattern type."""
    categories = defaultdict(list)
    
    for eid in sorted(effect_ids):
        parts = eid.split('_')
        
        if len(parts) >= 2:
            if parts[0] == 'heal':
                categories['Healing'].append(eid)
            elif parts[0] == 'restore':
                categories['Resource Restore'].append(eid)
            elif parts[1] == 'boost':
                categories['Stat Boosts'].append(eid)
            elif parts[1] == 'damage':
                categories['Damage Bonuses'].append(eid)
            elif parts[1] == 'resist':
                categories['Resistances'].append(eid)
            elif parts[1] == 'regen':
                categories['Regeneration'].append(eid)
            elif parts[1] == 'chance':
                categories['Chance Effects'].append(eid)
            elif parts[1] == 'penetration':
                categories['Penetration'].append(eid)
            elif parts[1] == 'reduction':
                categories['Cost Reduction'].append(eid)
            elif parts[0] == 'flat':
                categories['Flat Damage'].append(eid)
            elif parts[0] == 'magic':
                categories['Magic Effects'].append(eid)
            elif parts[0] in ['slow', 'stun', 'poison', 'burn']:
                categories['Status Effects'].append(eid)
            else:
                categories['Special/Complex'].append(eid)
        else:
            categories['Simple'].append(eid)
    
    return dict(categories)


def main():
    print("🔍 EFFECT ID VALIDATION")
    print("=" * 50)
    
    # Extract all effect IDs
    effect_ids_by_item = extract_all_effect_ids()
    if not effect_ids_by_item:
        return
    
    # Get all unique effect IDs
    all_effect_ids = set()
    for effect_list in effect_ids_by_item.values():
        all_effect_ids.update(effect_list)
    
    # Categorize effects
    categories = categorize_effect_ids(all_effect_ids)
    
    print("\\n📋 EFFECT ID CATEGORIES:")
    for category, effects in categories.items():
        print(f"\\n{category} ({len(effects)} effects):")
        for effect in effects:
            print(f"   • {effect}")
    
    print(f"\\n🧪 VALIDATION RESULTS:")
    print("-" * 40)
    
    valid_effects = []
    invalid_effects = []
    
    # Validate each effect ID
    for effect_id in sorted(all_effect_ids):
        is_valid, message, effect = validate_effect_id(effect_id)
        
        if is_valid:
            valid_effects.append((effect_id, effect))
            print(f"✅ {effect_id:25} -> {effect.__class__.__name__}")
        else:
            invalid_effects.append((effect_id, message))
            print(f"❌ {effect_id:25} -> {message}")
    
    # Summary
    print(f"\\n" + "=" * 50)
    print(f"📊 VALIDATION SUMMARY:")
    print(f"   • Total Effects: {len(all_effect_ids)}")
    print(f"   • Valid Effects: {len(valid_effects)}")
    print(f"   • Invalid Effects: {len(invalid_effects)}")
    print(f"   • Success Rate: {len(valid_effects)/len(all_effect_ids)*100:.1f}%")
    
    if invalid_effects:
        print(f"\\n❌ INVALID EFFECTS NEED ATTENTION:")
        for effect_id, reason in invalid_effects:
            print(f"   • {effect_id}: {reason}")
            
            # Show which items use this invalid effect
            items_using = [item for item, effects in effect_ids_by_item.items() 
                          if effect_id in effects]
            if items_using:
                print(f"     Used by: {', '.join(items_using[:3])}{'...' if len(items_using) > 3 else ''}")
    
    if len(invalid_effects) == 0:
        print("\\n🎉 ALL EFFECT IDS ARE VALID!")
    
    return len(invalid_effects) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
