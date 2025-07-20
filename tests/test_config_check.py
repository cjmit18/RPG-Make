#!/usr/bin/env python3

"""
Quick test to verify iron_dagger configuration.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_iron_dagger_config():
    """Check the iron_dagger configuration."""
    
    from game_sys.items.factory import ItemFactory
    
    print("Testing iron_dagger configuration...")
    
    dagger = ItemFactory.create('iron_dagger')
    if dagger:
        print(f"✓ Created iron dagger")
        print(f"  - Name: {dagger.name}")
        print(f"  - Type: {getattr(dagger, 'type', 'Unknown')}")
        print(f"  - Slot: {dagger.slot}")
        print(f"  - Slot Restriction: {getattr(dagger, 'slot_restriction', 'None')}")
        print(f"  - Dual Wield: {getattr(dagger, 'dual_wield', False)}")
        
        if dagger.slot == "weapon" and getattr(dagger, 'slot_restriction', '') == "either_hand":
            print("✓ Configuration is CORRECT")
            return True
        else:
            print("✗ Configuration is INCORRECT")
            return False
    else:
        print("✗ Failed to create iron dagger")
        return False

if __name__ == "__main__":
    success = test_iron_dagger_config()
    sys.exit(0 if success else 1)
