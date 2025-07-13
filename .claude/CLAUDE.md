# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

**Actor Hierarchy**: Core character system with RPG stats
- Primary stats (strength, dexterity, etc.) drive derived stats (health, attack, etc.)
- All stat calculations configurable via multipliers in settings
- Character creation via templates: `create_character("hero")`

**Effect System**: Flexible status effects and enchantments
- Effect Factory creates effects from IDs like "fire_damage_10"
- Equipment effects automatically applied through ScalingManager
- Temporary status effects managed by status_manager

### Core Modules

**Character System** (`game_sys/character/`)
- `actor.py` - Core Actor class with stats, inventory, combat integration
- `character_factory.py` - Template-based character creation
- `leveling_manager.py` - Experience and stat allocation
- `job_manager.py` - Class/job system with equipment restrictions

**Combat System** (`game_sys/combat/`)
- `engine.py` - Turn-based combat mechanics
- `combat_service.py` - Business logic layer for combat operations
- `damage_packet.py` - Standardized damage with types and modifiers
- `capabilities.py` - Combat abilities and skills

**Configuration** (`game_sys/config/`)
- `config_manager.py` - Centralized configuration access
- `default_settings.json` - Master configuration with feature toggles
- `feature_flags.py` - Runtime feature toggle checking

**Items & Equipment** (`game_sys/items/`)
- `factory.py` - Registry-based item creation
- `weapon.py`, `armor.py` - Equipment with stats and enchantments
- `equipment.py` - Equipment slot management
- `usage_manager.py` - Item usage and consumption

**Magic System** (`game_sys/magic/`)
- `spell_system.py` - Spell casting mechanics
- `enchanting_system.py` - Equipment enhancement
- `combo.py` - Multi-spell combinations

**Effects** (`game_sys/effects/`)
- `factory.py` - Dynamic effect creation
- `status_manager.py` - Temporary effect management
- `base.py` - Effect base classes

### Documentation Structure

**Critical**: Always consult these directories before implementing features:

- `docs/` - Technical documentation, architecture guides, implementation summaries
- `instructions/` - Step-by-step workflows for specific features  
- `examples/` - Working code samples demonstrating proper usage patterns

**Workflow**: Check `docs/` for architecture → `instructions/` for implementation → `examples/` for code patterns

### Testing Strategy

**Comprehensive Testing**: Multiple test approaches
- `tests/test_comprehensive.py` - Interactive test manager with tabbed UI
- `tests/run_all_tests.py` - Automated test suite runner
- Individual test files for specific components
- Demo applications serve as integration tests

**Test Categories**:
- Unit tests for individual components
- Integration tests for system interactions
- Configuration validation tests
- UI/demo-driven manual testing

### Configuration Management

**Feature Toggles**: All major systems controlled by toggles in `default_settings.json`
```python
# Check if feature enabled before use
if ConfigManager().get('toggles.ai', False):
    # AI system code
```

**Hierarchical Settings**: Nested configuration with fallbacks
```python
cfg = ConfigManager()
xp_multiplier = cfg.get('constants.leveling.xp_multiplier', 1.0)
combat_settings = cfg.get('combat.damage_calculation', {})
```

### Logging System

**Integrated Logging**: Consistent logging throughout all components
```python
from game_sys.logging import get_logger
logger = get_logger(__name__)
logger.info("Message")  # Outputs to console and JSON logs
```

**Centralized Configuration**: Log levels and outputs managed in logging module

### UI Architecture

**Tabbed Interface System**: Modern UI with multiple tabs
- Tab-based organization for different game features
- Dark/light mode toggle support
- Scrollable content areas
- Service layer integration (UI calls business logic, never direct manipulation)

**Demo Integration**: `demo.py` provides comprehensive UI for testing all systems

## Development Workflow

### Adding New Features
1. Check `docs/` for architectural guidance
2. Review `instructions/` for implementation patterns
3. Use `examples/` for code patterns  
4. Add feature toggle to `default_settings.json`
5. Create service class for business logic
6. Add factory pattern if object creation needed
7. Update UI to call service methods
8. Add tests (unit + demo integration)
9. Update documentation

### Code Standards
- Follow existing patterns and conventions
- Use service layer for all business logic
- Leverage existing factories for object creation
- Follow JSON schema patterns for new data
- Test through demo interface for integration validation
- Use appropriate logging levels throughout
- Never commit without running tests

### Critical Reminders
- Always check feature toggles before implementing optional systems
- Use ConfigManager for all configuration access
- Follow the Actor → Service → Factory → UI pattern
- Maintain JSON schema consistency
- Update both automated tests and demo functionality
- Document in appropriate folder (`docs/`, `instructions/`, or `examples/`)