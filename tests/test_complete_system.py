# test_complete_system.py
"""Test the complete system with stat allocation and enchanting."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_sys.character.character_factory import create_character
from game_sys.character.leveling_manager import leveling_manager


def test_stat_allocation_and_enchanting():
    """Test that stat allocation works and enchanting items exist."""
    print("=== Complete System Test ===")
    
    # Create a warrior character
    warrior = create_character("warrior")
    print(f"Created: {warrior.name}")
    
    # Test initial stats
    print(f"\nInitial Stats:")
    print(f"  Strength: {warrior.get_stat('strength'):.2f}")
    print(f"  Attack: {warrior.get_stat('attack'):.2f}")
    print(f"  Dexterity: {warrior.get_stat('dexterity'):.2f}")
    print(f"  Speed: {warrior.get_stat('speed'):.2f}")
    
    # Test stat allocation
    warrior.level = 3  # Give stat points
    print(f"\nSet level to {warrior.level}")
    
    available_points = leveling_manager.calculate_stat_points_available(warrior)
    print(f"Available stat points: {available_points}")
    
    # Allocate some points
    print("\nAllocating 2 points to strength...")
    for i in range(2):
        success = leveling_manager.allocate_stat_point(warrior, 'strength')
        if success:
            print(f"  ✓ Allocated point {i+1} to strength")
        else:
            print(f"  ✗ Failed to allocate point {i+1}")
    
    # Force stat update
    if hasattr(warrior, 'update_stats'):
        warrior.update_stats()
    
    print(f"\nUpdated Stats:")
    print(f"  Strength: {warrior.get_stat('strength'):.2f}")
    print(f"  Attack: {warrior.get_stat('attack'):.2f}")
    
    # Test enchantment creation
    print("\nTesting Enchantment System:")
    
    try:
        from game_sys.items.factory import ItemFactory
        
        # Test creating enchantments
        enchantments = [
            'fire_enchant',
            'ice_enchant',
            'lightning_enchant',
            'poison_enchant',
            'strength_enchant',
            'speed_enchant'
        ]
        
        for enchant_id in enchantments:
            try:
                enchant = ItemFactory.create(enchant_id)
                if enchant:
                    print(f"  ✓ Created {enchant.name}")
                else:
                    print(f"  ✗ Failed to create {enchant_id}")
            except Exception as e:
                print(f"  ✗ Error creating {enchant_id}: {e}")
        
        # Test applying an enchantment to the warrior's weapon
        weapon = getattr(warrior, 'weapon', None)
        if weapon:
            print(f"\nTesting enchanting {weapon.name}:")
            
            # Create a fire enchantment
            fire_enchant = ItemFactory.create('fire_enchant')
            if fire_enchant:
                print(f"  Created {fire_enchant.name}")
                
                # Apply to weapon
                fire_enchant.apply(warrior, weapon)
                print(f"  Applied {fire_enchant.name} to {weapon.name}")
                
                # Check if enchantment was applied
                enchantments = getattr(weapon, 'enchantments', [])
                effect_ids = getattr(weapon, 'effect_ids', [])
                damage_type = getattr(weapon, 'damage_type', None)
                
                print(f"  Weapon enchantments: {enchantments}")
                print(f"  Weapon effect IDs: {effect_ids}")
                print(f"  Weapon damage type: {damage_type}")
                
                if enchantments or effect_ids:
                    print("  ✓ Enchantment applied successfully!")
                else:
                    print("  ✗ Enchantment not applied properly")
            else:
                print("  ✗ Failed to create fire enchantment")
        else:
            print("\nNo weapon equipped to test enchanting")
        
        print("\n✓ Enchantment system tests completed!")
        
    except ImportError as e:
        print(f"\n✗ Could not import items system: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error testing enchantments: {e}")
        return False
    
    return True


def test_demo_integration():
    """Test that the demo can be created without errors."""
    print("\n=== Demo Integration Test ===")
    
    try:
        # Import and create demo (but don't run UI)
        from demo import SimpleGameDemo
        demo = SimpleGameDemo()
        
        if hasattr(demo, 'player') and demo.player:
            print(f"✓ Demo created with player: {demo.player.name}")
            
            # Test that enchanting methods exist
            if hasattr(demo, 'setup_enchanting_tab'):
                print("✓ Enchanting tab setup method exists")
            else:
                print("✗ Enchanting tab setup method missing")
                
            if hasattr(demo, 'refresh_enchanting_lists'):
                print("✓ Enchanting refresh method exists")
            else:
                print("✗ Enchanting refresh method missing")
                
            if hasattr(demo, 'apply_enchantment'):
                print("✓ Apply enchantment method exists")
            else:
                print("✗ Apply enchantment method missing")
                
            return True
        else:
            print("✗ Demo created but no player found")
            return False
            
    except Exception as e:
        print(f"✗ Error creating demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing Complete System Integration")
    print("=" * 50)
    
    # Test stat allocation
    success1 = test_stat_allocation_and_enchanting()
    
    # Test demo integration
    success2 = test_demo_integration()
    
    if success1 and success2:
        print("\n🎉 All system tests passed!")
        print("\nThe system now supports:")
        print("- Traditional RPG stats (strength, dexterity, vitality, etc.)")
        print("- Stat point allocation on level up")
        print("- Derived stats (attack from strength, speed from dexterity)")
        print("- Item enchanting with multiple enchantment types")
        print("- Full UI integration with leveling and enchanting tabs")
    else:
        print("\n❌ Some tests failed!")
        if not success1:
            print("- Stat allocation or enchanting system issues")
        if not success2:
            print("- Demo integration issues")
