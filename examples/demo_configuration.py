#!/usr/bin/env python3
"""
Configuration Integration Demo
Shows the legacy configuration system integration with character stats
"""
import asyncio
from rpg_engine.core.config import get_config, Rarity, Grade

def main():
    """Demonstrate configuration integration"""
    print("🎯 Configuration Integration Demo")
    print("=" * 60)
    
    # Load configuration
    config = get_config()
    
    print(f"\n✅ Configuration loaded from default_settings.json")
    print(f"   - Max Level: {config.leveling_config.max_level}")
    print(f"   - Base XP: {config.leveling_config.xp_base}")
    print(f"   - XP Growth: {config.leveling_config.growth_factor}")
    print(f"   - Stat Points/Level: {config.leveling_config.stat_points_per_level}")
    
    print(f"\n📊 Stat Calculation Formulas:")
    print(f"   - Health: {config.derived_formulas.health}x constitution")
    print(f"   - Mana: {config.derived_formulas.mana}x intelligence")
    print(f"   - Attack: {config.derived_formulas.attack}x strength")
    print(f"   - Magic Power: {config.derived_formulas.magic_power}x intelligence")
    print(f"   - Critical Chance: {config.derived_formulas.critical_chance}x luck (%)")
    print(f"   - Magic Resistance: {config.derived_formulas.magic_resistance}x wisdom (%)")
    
    print(f"\n🌟 Rarity System Multipliers:")
    rarities = [Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY, Rarity.MYTHIC, Rarity.DIVINE]
    for rarity in rarities:
        mult = config.get_rarity_multiplier(rarity)
        print(f"   - {rarity.value}: +{mult:.1%} stats")
    
    print(f"\n⭐ Grade System Multipliers:")
    grades = [Grade.ONE, Grade.TWO, Grade.THREE, Grade.FOUR, Grade.FIVE, Grade.SIX, Grade.SEVEN]
    for grade in grades:
        mult = config.get_grade_multiplier(grade)
        print(f"   - {grade.value}: +{mult:.1%} stats")
    
    print(f"\n💪 Experience Requirements (Sample Levels):")
    levels = [1, 5, 10, 25, 50, 100]
    for level in levels:
        exp = config.calculate_experience_for_level(level)
        print(f"   - Level {level}: {exp:,} XP")
    
    print(f"\n🎮 Combat Constants:")
    stamina_costs = config.get_stamina_costs()
    for action, cost in stamina_costs.items():
        print(f"   - {action.title()}: {cost} stamina")
    
    print("\n🎉 Configuration Integration Complete!")
    print("The character system now uses all values from default_settings.json")
    print("including sophisticated stat calculations, rarity/grade systems,")
    print("and configurable progression mechanics from the legacy codebase.")

if __name__ == "__main__":
    main()
