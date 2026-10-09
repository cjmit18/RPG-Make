"""
GitHub Workflow Components Test

This script tests all the components referenced in our updated GitHub workflows
to ensure they work correctly before deploying the CI/CD pipeline.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_github_workflow_components():
    """Test all components referenced in GitHub workflows"""
    print('🧪 Testing GitHub Workflow Components...')
    print()
    
    # Test 1: Core imports
    try:
        from rpg_engine.core.event_bus import EventBus
        from rpg_engine.core.config import GameConfig
        from rpg_engine.core.template_loader import TemplateManager
        from rpg_engine.systems.achievements import AchievementSystem
        from rpg_engine.systems.notifications import NotificationSystem
        print('✅ All core engine imports successful')
    except Exception as e:
        print(f'❌ Import error: {e}')
        return False
    
    # Test 2: Template system
    try:
        from rpg_engine.core.template_loader import get_template_manager
        tm = get_template_manager()
        stats = tm.get_template_stats()
        print(f'✅ Template system: {stats["total_templates"]} templates loaded')
        assert stats['character_templates'] > 0, 'No character templates loaded'
        assert stats['achievement_templates'] > 0, 'No achievement templates loaded'
        print(f'   - Character Templates: {stats["character_templates"]}')
        print(f'   - Achievement Templates: {stats["achievement_templates"]}')
    except Exception as e:
        print(f'❌ Template system error: {e}')
        return False

    # Test 3: Configuration system
    try:
        from rpg_engine.core.config import GameConfig
        config = GameConfig()
        raw_config = config.get_raw_config()
        assert 'character_mechanics' in raw_config, 'Character mechanics config missing'
        assert 'derived_stat_formulas' in raw_config['character_mechanics'], 'Derived stat formulas missing'
        print('✅ Configuration system working')
        
        # Show some derived stat formulas
        formulas = raw_config['character_mechanics']['derived_stat_formulas']
        print(f'   - Health formula: constitution × {formulas.get("health", "?")}')
        print(f'   - Mana formula: intelligence × {formulas.get("mana", "?")}')
    except Exception as e:
        print(f'❌ Configuration error: {e}')
        return False

    # Test 4: Observer pattern systems (async test)
    try:
        import asyncio
        from rpg_engine.systems.achievements.achievement_system import AchievementSystem
        from rpg_engine.systems.notifications.notification_system import NotificationSystem
        from rpg_engine.core.event_bus import EventBus
        from rpg_engine.core.config import GameConfig
        
        async def test_observers():
            event_bus = EventBus()
            config = GameConfig()
            
            # Test achievement system (initializes in constructor)
            achievement_system = AchievementSystem(event_bus, config)
            
            # Test notification system (initializes in constructor)
            notification_system = NotificationSystem(event_bus)
            
            return True
        
        # Run async test
        result = asyncio.run(test_observers())
        if result:
            print('✅ Observer pattern systems working')
        else:
            print('❌ Observer pattern systems failed')
            return False
            
    except Exception as e:
        print(f'❌ Observer pattern error: {e}')
        return False

    # Test 5: Character stat calculations
    try:
        tm = get_template_manager()
        warrior = tm.get_character_template('warrior_basic')
        if warrior:
            # Test stat calculation
            strength_1 = warrior.calculate_stat_at_level('strength', 1)
            strength_10 = warrior.calculate_stat_at_level('strength', 10)
            expected_10 = 16 + (1.3 * 9)  # base + (growth * (level - 1))
            
            assert abs(strength_10 - expected_10) < 0.001, 'Stat calculation error'
            print('✅ Character stat calculations working')
            print(f'   - Warrior Level 1 Strength: {strength_1}')
            print(f'   - Warrior Level 10 Strength: {strength_10}')
        else:
            print('❌ Warrior template not found')
            return False
    except Exception as e:
        print(f'❌ Stat calculation error: {e}')
        return False

    # Test 6: JSON data integrity
    try:
        import json
        
        # Test character templates JSON
        with open('data/character_templates.json', 'r') as f:
            templates = json.load(f)
            assert 'character_templates' in templates
            template_count = len(templates['character_templates'])
            print(f'✅ Character templates JSON valid ({template_count} templates)')
        
        # Test achievements JSON
        with open('data/achievements.json', 'r') as f:
            achievements = json.load(f)
            assert 'achievements' in achievements
            print('✅ Achievements JSON valid')
            
        # Test configuration JSON
        with open('config/default_settings.json', 'r') as f:
            config = json.load(f)
            assert 'character_mechanics' in config
            print('✅ Configuration JSON valid')
            
    except Exception as e:
        print(f'❌ JSON data integrity error: {e}')
        return False

    print()
    print('🎉 All GitHub workflow components verified successfully!')
    print()
    print('📋 Workflow Components Status:')
    print('   ✅ Core engine imports')
    print('   ✅ Template loading system')
    print('   ✅ Configuration system')
    print('   ✅ Observer pattern systems')
    print('   ✅ Character stat calculations')
    print('   ✅ JSON data integrity')
    print()
    print('🚀 GitHub workflows are ready to run!')
    
    return True

if __name__ == "__main__":
    success = test_github_workflow_components()
    exit(0 if success else 1)
