"""
Character Creation and Stat Calculation Demo

This demonstrates the complete data-driven character system
with proper stat calculations using templates and formulas.
"""
import sys
from pathlib import Path
import logging
import asyncio
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from rpg_engine.core.template_loader import (
    TemplateManager, 
    CharacterTemplate, 
    get_template_manager
)
from rpg_engine.core.config import GameConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CharacterCreationDemo:
    """Demo showing character creation and stat calculations"""
    
    def __init__(self):
        self.template_manager = get_template_manager()
        self.config = GameConfig()
        
    async def run_demo(self):
        """Run the character creation demonstration"""
        print("🧙‍♂️ CHARACTER CREATION & STAT SYSTEM DEMO")
        print("=" * 50)
        
        # Show available templates
        await self.show_available_templates()
        
        # Create and demo characters from templates
        await self.demo_character_creation()
        
        # Show stat progression examples
        await self.demo_stat_progression()
        
        # Show derived stat calculations
        await self.demo_derived_stats()
        
        print("\n✨ Demo completed successfully! ✨")
    
    async def show_available_templates(self):
        """Show all available character templates"""
        print("\n📋 AVAILABLE CHARACTER TEMPLATES:")
        print("-" * 35)
        
        templates = self.template_manager.list_character_templates()
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template.name} ({template.character_class})")
            print(f"   Rarity: {template.rarity} | Grade: {template.grade}")
            print(f"   Description: {template.description}")
            print()
    
    async def demo_character_creation(self):
        """Demo creating characters from templates"""
        print("\n⚔️ CHARACTER CREATION EXAMPLES:")
        print("-" * 35)
        
        # Get a few example templates
        templates = self.template_manager.list_character_templates()[:3]
        
        for template in templates:
            print(f"\n🏷️ Creating: {template.name}")
            print(f"Class: {template.character_class}")
            print(f"Background: {template.background}")
            
            print("Starting Stats (Level 1):")
            for stat_name, base_value in template.base_stats.items():
                print(f"  {stat_name.capitalize()}: {base_value}")
            
            print("Growth Rates (per level):")
            for stat_name, growth_rate in template.growth_rates.items():
                print(f"  {stat_name.capitalize()}: +{growth_rate}")
            
            if template.starting_equipment:
                print(f"Starting Equipment: {', '.join(template.starting_equipment)}")
            
            if template.starting_skills:
                print(f"Starting Skills: {', '.join(template.starting_skills)}")
    
    async def demo_stat_progression(self):
        """Demo stat progression over levels"""
        print("\n📊 STAT PROGRESSION EXAMPLES:")
        print("-" * 35)
        
        # Use the warrior template for demonstration
        warrior = self.template_manager.get_character_template("warrior_basic")
        if not warrior:
            print("Warrior template not found!")
            return
        
        print(f"\n🛡️ {warrior.name} Stat Progression:")
        
        levels = [1, 5, 10, 20, 50]
        stats_to_show = ['strength', 'constitution', 'dexterity', 'intelligence']
        
        # Header
        print(f"{'Level':<8}", end="")
        for stat in stats_to_show:
            print(f"{stat.capitalize():<12}", end="")
        print()
        print("-" * 60)
        
        # Show progression
        for level in levels:
            print(f"{level:<8}", end="")
            for stat in stats_to_show:
                value = warrior.calculate_stat_at_level(stat, level)
                print(f"{value:<12.1f}", end="")
            print()
    
    async def demo_derived_stats(self):
        """Demo derived stat calculations"""
        print("\n⚗️ DERIVED STAT CALCULATIONS:")
        print("-" * 35)
        
        # Get derived stat formulas from config
        raw_config = self.config.get_raw_config()
        formulas = raw_config.get('character_mechanics', {}).get('derived_stat_formulas', {})
        
        if not formulas:
            print("No derived stat formulas found in configuration!")
            return
        
        print("Derived Stat Formulas:")
        for stat_name, multiplier in formulas.items():
            print(f"  {stat_name}: base_stat × {multiplier}")
        print()
        
        # Demo with warrior at level 10
        warrior = self.template_manager.get_character_template("warrior_basic")
        if not warrior:
            return
        
        level = 10
        print(f"🛡️ {warrior.name} at Level {level}:")
        print()
        
        # Show base stats first
        print("Base Stats:")
        base_stats = {}
        for stat_name in ['strength', 'constitution', 'intelligence', 'dexterity', 'vitality', 'wisdom']:
            value = warrior.calculate_stat_at_level(stat_name, level)
            base_stats[stat_name] = value
            print(f"  {stat_name.capitalize()}: {value:.1f}")
        print()
        
        # Show derived stats
        print("Derived Stats:")
        derived_examples = {
            'health': ('constitution', formulas.get('health', 10.0)),
            'mana': ('intelligence', formulas.get('mana', 5.0)),
            'stamina': ('vitality', formulas.get('stamina', 8.0)),
            'attack': ('strength', formulas.get('attack', 2.0)),
            'defense': ('constitution', formulas.get('defense', 1.5))
        }
        
        for derived_name, (base_stat, multiplier) in derived_examples.items():
            if base_stat in base_stats:
                base_value = base_stats[base_stat]
                derived_value = base_value * multiplier
                print(f"  {derived_name.capitalize()}: {derived_value:.1f} ({base_stat} × {multiplier})")
    
    async def demo_template_system_benefits(self):
        """Show benefits of the template system"""
        print("\n🎯 TEMPLATE SYSTEM BENEFITS:")
        print("-" * 35)
        
        benefits = [
            "✅ Data-driven: Easy to modify without code changes",
            "✅ Modular: Each template is independent",
            "✅ Extensible: Add new templates easily", 
            "✅ Balanced: Growth rates control progression",
            "✅ Flexible: Support for different rarities and grades",
            "✅ Validated: Automatic validation prevents errors",
            "✅ Hot-reloadable: Changes can be loaded at runtime"
        ]
        
        for benefit in benefits:
            print(benefit)
        
        stats = self.template_manager.get_template_stats()
        print(f"\nCurrent System Stats:")
        print(f"  📝 {stats['character_templates']} Character Templates")
        print(f"  🏆 {stats['achievement_templates']} Achievement Templates")
        print(f"  📊 {stats['total_templates']} Total Templates")

async def main():
    """Run the demonstration"""
    try:
        demo = CharacterCreationDemo()
        await demo.run_demo()
        await demo.demo_template_system_benefits()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.exception("Demo failure details:")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
