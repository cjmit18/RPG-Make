from game_sys.character.job_manager import JobManager
from game_sys.character.actor import Actor


def test_mage_staff():
    """Test mage with two-handed staff."""
    print("=== Testing Mage with Two-Handed Staff ===\n")
    
    # Create mage
    mage = Actor(
        name="Test Mage",
        base_stats={
            'health': 80,
            'mana': 100,
            'stamina': 60,
            'attack': 8,
            'defense': 4,
            'intellect': 15
        }
    )
    
    # Assign mage job
    JobManager.assign(mage, 'mage')
    print(f"Mage created with job: {getattr(mage, 'job_name', 'mage')}")
    
    # List starting items
    print("\nStarting inventory:")
    staff = None
    spell_focus = None
    
    for item in mage.inventory.list_items():
        print(f"  - {item.name} ({getattr(item, 'type', 'unknown')})")
        if hasattr(item, 'two_handed'):
            print(f"    Two-handed: {item.two_handed}")
        if hasattr(item, 'dual_wield'):
            print(f"    Dual wield: {item.dual_wield}")
        if hasattr(item, 'base_damage'):
            print(f"    Base damage: {item.base_damage}")
        
        if item.name == "Apprentice Staff":
            staff = item
        elif item.name == "Spell Focus":
            spell_focus = item
    
    # Try to equip spell focus first
    if spell_focus:
        success = mage.equip_offhand(spell_focus)
        print(f"\nEquipped spell focus first: {success}")
        print(f"Current offhand: {mage.offhand.name if mage.offhand else 'None'}")
    
    # Equip two-handed staff
    if staff:
        mage.equip_weapon(staff)
        print(f"Equipped two-handed staff: {staff.name}")
        print(f"Offhand after equipping staff: {mage.offhand.name if mage.offhand else 'None'}")
    
    # Try to equip offhand while holding two-handed weapon
    if spell_focus:
        success = mage.equip_offhand(spell_focus)
        print(f"Attempted to dual-wield with two-handed weapon: {success}")
    
    total_damage = mage.get_total_damage()
    print(f"\nTotal damage: {total_damage}")
    print("Test completed!")


if __name__ == "__main__":
    test_mage_staff()
