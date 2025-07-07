# examples/config_usage_example.py
"""
This script demonstrates how to use the updated configuration system.
It shows various methods to access configuration values and sections.
"""

from game_sys.config.config_manager import ConfigManager

def main():
    # Get the ConfigManager singleton instance
    cfg = ConfigManager()
    
    print("==== Configuration System Demo ====\n")
    
    # 1. Access specific configuration values with dot notation
    print("=== Example 1: Accessing specific values ===")
    max_level = cfg.get('constants.leveling.max_level')
    points_per_level = cfg.get('leveling.points_per_level')
    print(f"Max Level: {max_level}")
    print(f"Points Per Level: {points_per_level}")
    print()
    
    # 2. Access entire configuration sections
    print("=== Example 2: Accessing entire sections ===")
    # Get all spells
    spells = cfg.get_section('spells')
    print(f"Available Spells: {', '.join(spells.keys())}")
    
    # Get all skills
    skills = cfg.get_section('skills')
    print(f"Available Skills: {', '.join(skills.keys())}")
    print()
    
    # 3. Using default values when configuration doesn't exist
    print("=== Example 3: Using default values ===")
    # This key doesn't exist, so we'll get the default value
    custom_setting = cfg.get('nonexistent.key', 'Default Value')
    print(f"Custom Setting (with default): {custom_setting}")
    print()
    
    # 4. Get detailed information about a specific spell
    print("=== Example 4: Detailed spell information ===")
    fireball = spells.get('fireball', {})
    print(f"Fireball Spell:")
    print(f"  Name: {fireball.get('name')}")
    print(f"  Mana Cost: {fireball.get('mana_cost')}")
    print(f"  Base Damage: {fireball.get('base_damage')}")
    print(f"  Damage Type: {fireball.get('damage_type')}")
    print(f"  Range: {fireball.get('range')}")
    print(f"  Cooldown: {fireball.get('cooldown')}")
    print()
    
    # 5. Get detailed information about a specific enchantment
    print("=== Example 5: Detailed enchantment information ===")
    enchantments = cfg.get_section('enchantments')
    fire_enchant = enchantments.get('fire_enchant', {})
    print(f"Fire Enchantment:")
    print(f"  Name: {fire_enchant.get('name')}")
    print(f"  Level Req: {fire_enchant.get('level_requirement')}")
    print(f"  Description: {fire_enchant.get('description')}")
    
    # Get the effects of the enchantment
    effects = fire_enchant.get('effects', [])
    if effects:
        print(f"  Effects:")
        for effect in effects:
            print(f"    - Type: {effect.get('type')}")
            print(f"      Damage Type: {effect.get('damage_type')}")
            print(f"      Amount: {effect.get('amount')}")
            print(f"      Duration: {effect.get('duration')}")
    
if __name__ == "__main__":
    main()
