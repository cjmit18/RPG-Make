# COPILOT.md

This file provides guidance to GitHub Copilot when working with code in this repository.

## 🎯 Project Status: STABLE & OPERATIONAL ✅

**All 6 Major Architectural Tasks Implemented:**
1. ✅ **UI Management** - Enhanced service delegation with interactive equipment slots
2. ✅ **Game Logic Controllers** - Interface-compliant wrappers  
3. ✅ **Method Count Reduction** - Event-driven consolidation
4. ✅ **Clear Interfaces** - Type-safe contracts (200+ lines)
5. ✅ **Observer Pattern** - Event-driven UI updates with full integration
6. ✅ **Items System** - Complete 42-item database with smart auto-equipping

**Recent Critical Fixes (July 23, 2025):**
- ✅ **ServiceResult Compatibility** - Fixed "'ServiceResult' object is not subscriptable" errors
- ✅ **Character Creation System** - Fully functional stat allocation and template selection
- ✅ **UI Integration** - Character stats properly displayed next to allocation buttons
- ✅ **Service Layer Consistency** - All methods return standardized dictionary format
- ✅ **Documentation Updates** - Current project state and fixes documented

**Previous Achievements (July 2025):**
- ✅ **Documentation Organization** - All documentation properly organized in docs/ folder structure
- ✅ **Enhanced UI Service** - Interactive equipment slots with performance metrics
- ✅ **Clean Architecture** - Proper service layer separation maintained
- ✅ **Project Structure** - Clean root directory with organized documentation

## Common Commands

### Testing
```bash
# Run comprehensive test suite
python tests/test_comprehensive.py
python tests/run_all_tests.py

# Run observer pattern integration test
python test_observer_integration.py

# Run automated pytest tests
pytest --maxfail=1 --disable-warnings -q
pytest --cov=game_sys  # With coverage

# Run Windows batch test with UI
run_comprehensive_test_updated.bat
```

### Demo Applications
```bash
python demo.py           # Main tabbed demo with EVENT-DRIVEN UI updates
python playground.py     # Engine feature showcase and testing

# Test observer integration in demo:
# 1. Run demo.py
# 2. Go to Leveling tab
# 3. Try 'Learn Skill', 'Learn Spell', 'Gain XP (Test)'
# 4. Watch automatic UI updates via observer pattern!
```

### Code Quality
```bash
flake8                  # Linting
mypy .                  # Type checking
python fix_flake8.py    # Auto-fix common flake8 issues
```

## Architecture Overview

This is a comprehensive Python RPG engine (`game_sys/`) with **complete modern architecture** featuring event-driven UI updates, observer pattern integration, service-oriented design, and extensive JSON-driven configuration. The project showcases clean separation of concerns with dedicated modules for character management, combat, items, magic, effects, AI, and more.

### 🏗️ **Modern Architecture Stack**
- **Observer Pattern** - Event-driven UI updates with automatic refresh
- **Service Layer** - Clean business logic isolation  
- **Factory Pattern** - Registry-based object creation
- **Interface Design** - Complete type-safe contracts
- **Hook System** - Extensible event-driven architecture

### Key Design Patterns

**Event-Driven Architecture**: Complete observer pattern integration
- `GameEventPublisher` - Centralized event publishing for all game actions
- `UIObserver` - Automatic UI updates responding to game events
- `HooksEventManager` - Bridge between observer pattern and existing event bus
- Event-driven learning methods: `learn_skill_dialog()`, `learn_spell_dialog()`, `learn_enchant_dialog()`

**Service Layer Architecture**: Core business logic isolated in service classes
- `CombatService` - Centralized combat operations
- `CharacterFactory` - Template-based character creation  
- `ConfigManager` - Thread-safe singleton for all configuration
- `ItemFactory` - Registry-based item creation

**Observer Pattern Integration**: Modern event-driven UI updates
```python
# OLD WAY: Manual updates
self.log_message(f"Learned spell: {spell_id}!", "info")
self.update_progression_display()

# NEW WAY: Event-driven
GameEventPublisher.publish_spell_learned(spell_id, source=self)
# Observer automatically handles UI updates, logging, error handling
```

**JSON-Driven Configuration**: Everything configurable via `game_sys/*/data/` JSON files
- Character templates, jobs, items, spells, enchantments
- Feature toggles in `default_settings.json` control module activation
- Access config via `ConfigManager().get('path.to.setting')`

**Factory Pattern**: Centralized object creation with registry-based extensibility
- `CharacterFactory.create_character(template_name)` for characters
- `ItemFactory.create(item_name)` for items
- `EffectFactory.create_from_id(effect_id)` for effects

**Hook System**: Event-driven extension points with observer integration
- Engine emits events at key moments via `GameEventPublisher`
- Observer pattern enables automatic UI updates and error handling
- Modules register hooks to extend behavior without core modification
- Complete event-driven architecture ready for plugins and achievements

## 📚 Documentation Structure

The documentation is now organized into logical categories in the `docs/` folder:

- **📁 01-architecture/** - Core architectural documentation and project overview
- **📁 02-systems/** - Core system documentation and implementation guides  
- **📁 03-features/** - Game feature documentation and implementation
- **📁 04-testing/** - Testing documentation and quality assurance
- **📁 05-maintenance/** - Maintenance, cleanup, and refactoring documentation
- **📁 06-completed-tasks/** - Completed implementation tasks and milestones
- **📁 archive/** - Archived documentation and historical records

**Quick Reference**: See `docs/README.md` for complete documentation index.

## Core Modules

### Essential Systems
- `game_sys/core/` - Configuration, scaling, core engine
- `game_sys/character/` - Actor, character management, templates
- `game_sys/combat/` - Combat mechanics, damage, capabilities
- `game_sys/items/` - Item system, equipment, factories
- `game_sys/inventory/` - Inventory management and UI

### Observer Pattern Integration
- `interfaces/observer_interfaces.py` - Core observer pattern with hooks bridge
- `interfaces/ui_observer.py` - UIObserver with automatic event subscriptions
- `demo.py` - Enhanced with event-driven learning methods

### Optional Feature Modules
- `game_sys/magic/` - Spells, enchantments, magical effects
- `game_sys/ai/` - Enemy AI behaviors and decision making
- `game_sys/effects/` - Status effects, buffs, debuffs
- `game_sys/loot/` - Loot generation and distribution
- `game_sys/skills/` - Skill system and progression

## 🔧 Service Layer Best Practices (Updated July 2025)

### Critical Pattern: Dictionary Return Format
**ALWAYS return Dict[str, Any] from service methods, never ServiceResult objects**

```python
# ✅ CORRECT - UI Compatible
def allocate_stat_point(self, stat_name: str) -> Dict[str, Any]:
    try:
        # Business logic here
        if success:
            return {
                'success': True,
                'points_remaining': available_points,
                'message': f"Allocated point to {stat_name}"
            }
        else:
            return {
                'success': False,
                'error': 'Insufficient points',
                'message': 'Cannot allocate stat point'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Operation failed'
        }

# ❌ INCORRECT - Causes UI errors
def allocate_stat_point(self, stat_name: str) -> ServiceResult:
    return ServiceResult.success_result(...)  # UI can't subscript this!
```

### Service Method Completeness
**Ensure all UI callbacks have corresponding service methods**

```python
# UI callback registration requires these service methods:
service_methods_required = [
    'get_saved_character_list',     # Character library
    'save_current_character',       # Character saving  
    'delete_saved_character',       # Character deletion
    'toggle_admin_mode',           # Admin panel
    'get_character_stat_data',     # UI stat display
    'allocate_stat_point',         # Stat allocation
    'reset_stat_allocation'        # Stat reset
]
```

### Data Flow Pattern
```python
# Service Layer → Controller → UI (Standard Pattern)
# 1. Service returns Dict
service_result = self.character_service.allocate_stat_point(stat_name)

# 2. Controller checks success
if service_result['success']:
    self._update_character_display()
    self._update_stat_labels()
else:
    self._log_error(service_result['message'])

# 3. UI updates with formatted data
def _update_stat_labels(self):
    stat_data = self.character_service.get_character_stat_data()
    self.ui_service.update_stat_labels(stat_data)
```

## Development Guidelines

### Code Organization - Modern Architecture ✅
- **Event-driven UI updates** - Use `GameEventPublisher` for automatic UI refresh
- **Services contain business logic** - Keep core operations in service classes  
- **Service methods return Dict format** - Never return ServiceResult to UI layer
- **Observer pattern integration** - Leverage automatic UI updates and error handling
- **UI calls services** - Never put business logic in UI code
- **Factories create objects** - Use established factories for object creation
- **Configuration drives behavior** - Make features configurable via JSON

### Observer Pattern Usage (NEW!)
```python
# Event-driven approach for game actions
from interfaces.observer_interfaces import GameEventPublisher

def learn_new_skill(self, skill_id):
    # Business logic
    success = self.character.learn_skill(skill_id)
    
    # Event-driven UI updates
    if success:
        GameEventPublisher.publish_skill_learned(skill_id, source=self)
        # Observer automatically handles:
        # - UI progression display update
        # - Formatted log messages
        # - Error handling
    else:
        GameEventPublisher.publish_error(f"Failed to learn skill: {skill_id}", source=self)
```

### Testing Strategy
- **Observer integration tests** - Test event-driven functionality
- **Service layer tests** - Test business logic in isolation
- **Integration tests** - Test service interactions
- **Demo validation** - Ensure features work in main demo with event-driven updates
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

### Modern Event-Driven UI System ⭐ NEW!
- **Observer Pattern** - Automatic UI updates via event subscription
- **Tabbed interface** - `demo.py` provides comprehensive UI with event-driven updates
- **Service integration** - UI calls service methods, observers handle display updates
- **Event-driven responses** - UI automatically updates via GameEventPublisher events
- **State management** - Services maintain business state, observers handle UI state

### Modern UI Patterns (Event-Driven)
```python
# NEW: Event-driven UI pattern
def on_learn_skill_button(self):
    try:
        skill_id = self.get_selected_skill()
        
        # Business logic only
        success = self.character.learn_skill(skill_id)
        
        # Event-driven UI updates (automatic!)
        if success:
            GameEventPublisher.publish_skill_learned(skill_id, source=self)
            # Observer automatically handles:
            # - self.update_progression_display()
            # - self.log_message(f"Learned skill: {skill_id}!", "info")
        else:
            GameEventPublisher.publish_error(f"Failed to learn skill: {skill_id}", source=self)
            
    except Exception as e:
        GameEventPublisher.publish_error(f"Skill learning error: {e}", source=self)

# LEGACY: Manual UI pattern (still supported but not recommended)
def on_attack_button_legacy(self):
    try:
        # Get user selections
        target = self.get_selected_target()
        
        # Call service
        result = self.combat_service.execute_attack(
            self.player, target, self.player.weapon
        )
        
        # Manual display updates
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
### Adding New Features (Updated for Observer Pattern)
1. Add feature toggle to `default_settings.json`
2. Create service class for business logic
3. Add data files for configuration
4. Integrate with existing factories
5. Add event-driven UI integration to demo using `GameEventPublisher`
6. Write tests for service layer and observer integration
7. Update documentation in organized `docs/` structure

## Common Issues and Solutions

### Observer Pattern Integration
- Use `GameEventPublisher` for all UI-impacting game actions
- Import observer interfaces: `from interfaces.observer_interfaces import GameEventPublisher`
- Let observers handle UI updates automatically instead of manual refresh calls
- Test observer integration with `test_observer_integration.py`

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

### UI Responsiveness (Modern Approach)
- Use `GameEventPublisher` for automatic UI updates
- Let observer pattern handle UI refresh instead of manual calls
- Use try/catch for all service calls with event-driven error handling
- Provide user feedback through event publishing

## Git Integration Guidelines

When GitHub Copilot suggests code changes:

When GitHub Copilot suggests code changes:

1. **Follow Architecture Patterns**: Ensure suggestions align with modern event-driven architecture and observer pattern
2. **Maintain Configuration**: Keep features configurable via JSON
3. **Preserve Factory Pattern**: Use existing factories for object creation
4. **Use Observer Pattern**: Prefer event-driven UI updates via `GameEventPublisher`
5. **Test Integration**: Ensure suggestions work with existing test suite and observer integration
6. **Demo Compatibility**: Verify suggestions work in main demo interface with event-driven updates

## Quick Reference

### Essential Imports (Updated)
```python
# Core architecture
from game_sys.config.config_manager import ConfigManager
from game_sys.character.character_factory import CharacterFactory
from game_sys.items.item_factory import ItemFactory
from game_sys.combat.combat_service import CombatService
from game_sys.logging import get_logger

# Observer pattern (NEW!)
from interfaces.observer_interfaces import GameEventPublisher
from interfaces.ui_observer import UIObserver
```

### Common Operations (Event-Driven)
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

# Event-driven UI updates (NEW!)
GameEventPublisher.publish_skill_learned(skill_id, source=self)
GameEventPublisher.publish_spell_learned(spell_id, source=self)
GameEventPublisher.publish_level_up(new_level, source=self)
GameEventPublisher.publish_error(error_message, source=self)

# Logging
logger = get_logger(__name__)
logger.info("Operation completed")
```

---

**📊 Project Status: COMPLETE MODERN ARCHITECTURE**
- ✅ All 5 architectural tasks implemented and validated
- ✅ Event-driven UI updates operational in demo
- ✅ Observer pattern integration complete with testing
- ✅ Documentation organized and comprehensive
- ✅ Ready for advanced features and plugin development
