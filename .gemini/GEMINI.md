# GEMINI.md

This file provides guidance to Gemini Code Assist when working with code in this repository.

## Common Commands

### Testing
```bash
# Run comprehensive test suite
python tests/test_comprehensive.py
python tests/run_all_tests.py

# Run automated pytest tests
pytest --maxfail=1 --disable-warnings -q
pytest --cov=game_sys  # With coverage

# Run Windows batch test with UI
run_comprehensive_test_updated.bat
```

### Demo Applications
```bash
python demo.py           # Main tabbed demo with character creation, combat, inventory
python playground.py     # Engine feature showcase and testing
```

### Code Quality
```bash
flake8                  # Linting
mypy .                  # Type checking
python fix_flake8.py    # Auto-fix common flake8 issues
```

## Architecture Overview

This is a comprehensive Python RPG engine (`game_sys/`) with modular JSON-driven configuration, extensive UI system, and service-oriented architecture. The project emphasizes clean separation of concerns with dedicated modules for character management, combat, items, magic, effects, AI, and more.

### Key Design Patterns

**Service Layer Architecture**: Core business logic isolated in service classes
- `CombatService` - Centralized combat operations
- `CharacterFactory` - Template-based character creation  
- `ConfigManager` - Thread-safe singleton for all configuration
- `ItemFactory` - Registry-based item creation

**JSON-Driven Configuration**: Everything configurable via `game_sys/*/data/` JSON files
- Character templates, jobs, items, spells, enchantments
- Feature toggles in `default_settings.json` control module activation
- Access config via `ConfigManager().get('path.to.setting')`

**Factory Pattern**: Centralized object creation with registry-based extensibility
- `CharacterFactory.create_character(template_name)` for characters
- `ItemFactory.create(item_name)` for items
- `EffectFactory.create_from_id(effect_id)` for effects

**Hook System**: Event-driven extension points
- Engine emits events at key moments
- Modules register hooks to extend behavior
- Clean way to add features without modifying core

## Core Modules

### Essential Systems
- `game_sys/core/` - Configuration, scaling, core engine
- `game_sys/character/` - Actor, character management, templates
- `game_sys/combat/` - Combat mechanics, damage, capabilities
- `game_sys/items/` - Item system, equipment, factories
- `game_sys/inventory/` - Inventory management and UI

### Optional Feature Modules
- `game_sys/magic/` - Spells, enchantments, magical effects
- `game_sys/ai/` - Enemy AI behaviors and decision making
- `game_sys/effects/` - Status effects, buffs, debuffs
- `game_sys/loot/` - Loot generation and distribution
- `game_sys/skills/` - Skill system and progression

## Development Guidelines

### Code Organization
- **Services contain business logic** - Keep core operations in service classes
- **UI calls services** - Never put business logic in UI code
- **Factories create objects** - Use established factories for object creation
- **Configuration drives behavior** - Make features configurable via JSON

### Testing Strategy
- **Service layer tests** - Test business logic in isolation
- **Integration tests** - Test service interactions
- **Demo validation** - Ensure features work in main demo
- **UI regression tests** - Validate UI behavior with automated tests

### Configuration Pattern
```python
from game_sys.config.config_manager import ConfigManager

cfg = ConfigManager()
# Check if feature is enabled
if cfg.get('features.magic.enabled', True):
    # Feature implementation
    
# Get configuration values
multiplier = cfg.get('constants.damage.base_multiplier', 1.0)
templates = cfg.get('data.character_templates', {})
```

### Service Pattern
```python
# Good: Use service layer
from game_sys.combat.combat_service import CombatService

combat_service = CombatService()
result = combat_service.execute_attack(attacker, defender, weapon)

# Bad: Direct manipulation
attacker.attack(defender)  # Bypasses business logic
```

### Factory Pattern
```python
# Good: Use factories
from game_sys.character.character_factory import CharacterFactory
from game_sys.items.item_factory import ItemFactory

character = CharacterFactory.create_character('warrior_template')
weapon = ItemFactory.create('iron_sword')

# Bad: Direct instantiation
character = Actor(name='Test')  # Missing template application
```

## UI Integration

### Tkinter UI System
- **Tabbed interface** - `demo.py` provides comprehensive UI
- **Service integration** - UI calls service methods, displays results
- **Event handling** - UI responds to user actions, updates display
- **State management** - UI maintains display state, services maintain business state

### UI Patterns
```python
# UI Method Pattern
def on_attack_button(self):
    try:
        # Get user selections
        target = self.get_selected_target()
        
        # Call service
        result = self.combat_service.execute_attack(
            self.player, target, self.player.weapon
        )
        
        # Update display
        self.update_combat_log(result.message)
        self.refresh_health_bars()
        
    except Exception as e:
        self.show_error(f"Attack failed: {e}")
```

## Testing Integration

### Test Structure
- `tests/` - Core test files
- `test_comprehensive.py` - Main integration test suite
- Individual service tests validate business logic
- UI tests ensure interface functionality

### Demo Integration
- All features must work in `demo.py`
- Demo serves as integration test and user showcase
- Service methods should be demonstrable through UI

## Configuration Files

### Key Configuration Files
- `game_sys/config/default_settings.json` - Feature toggles and defaults
- `game_sys/character/data/character_templates.json` - Character templates
- `game_sys/items/data/items.json` - Item definitions
- `game_sys/magic/data/spells.json` - Spell definitions
- `game_sys/effects/data/effects.json` - Effect definitions

### Adding New Features
1. Add feature toggle to `default_settings.json`
2. Create service class for business logic
3. Add data files for configuration
4. Integrate with existing factories
5. Add UI integration to demo
6. Write tests for service layer
7. Update documentation

## Common Issues and Solutions

### Import Cycles
- Use `from __future__ import annotations`
- Use `TYPE_CHECKING` for type hints
- Delay imports to avoid cycles

### Configuration Access
- Always use `ConfigManager()` singleton
- Provide sensible defaults for all config reads
- Use dot notation for nested config access

### Service Integration
- Services should be stateless where possible
- Pass dependencies explicitly
- Use dependency injection for testing

### UI Responsiveness
- Use try/catch for all service calls
- Provide user feedback for long operations
- Update UI state after service operations

## Git Integration Guidelines

When Gemini suggests code changes:

1. **Follow Architecture Patterns**: Ensure suggestions align with service layer architecture
2. **Maintain Configuration**: Keep features configurable via JSON
3. **Preserve Factory Pattern**: Use existing factories for object creation
4. **Test Integration**: Ensure suggestions work with existing test suite
5. **Demo Compatibility**: Verify suggestions work in main demo interface

## Quick Reference

### Essential Imports
```python
from game_sys.config.config_manager import ConfigManager
from game_sys.character.character_factory import CharacterFactory
from game_sys.items.item_factory import ItemFactory
from game_sys.combat.combat_service import CombatService
from game_sys.logging import get_logger
```

### Common Operations
```python
# Configuration
cfg = ConfigManager()
setting = cfg.get('path.to.setting', default_value)

# Character Creation
character = CharacterFactory.create_character('template_name')

# Item Creation
item = ItemFactory.create('item_name')

# Combat
combat_service = CombatService()
result = combat_service.execute_attack(attacker, defender, weapon)

# Logging
logger = get_logger(__name__)
logger.info("Operation completed")
```