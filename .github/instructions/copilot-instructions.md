# RPG Game Engine - AI Coding Assistant Instructions

## Project Documentation Structure

**CRITICAL**: Always consult these directories before implementing features:

### 📁 `docs/` - Technical Documentation
- **Architecture guides** - System design and integration patterns
- **Implementation summaries** - Completed feature documentation
- **Testing guides** - Comprehensive testing strategies
- **Fix reports** - Solutions to known issues and bugs
- **Examples**: `AI_ARCHITECTURE.md`, `CONFIG_SYSTEM_README.md`, `DEMO_README.md`

### 📁 `instructions/` - Implementation Guides
- **Step-by-step workflows** for specific features
- **Integration instructions** for complex systems
- **Examples**: `combo_bar_and_tab_implementation.md`, `STAMINA_USAGE_FOR_COMBAT_ACTIONS.md`

### 📁 `examples/` - Code Examples
- **Working code samples** demonstrating proper usage patterns
- **Configuration examples** showing best practices
- **Examples**: `config_usage_example.py`

**WORKFLOW**: When implementing any feature, first check `docs/` for architecture guidance, then `instructions/` for implementation steps, then `examples/` for code patterns.

## Architecture Overview

This is a modular Python RPG engine (`game_sys/`) with extensive JSON-driven configuration, UI system, and service-oriented architecture. The project emphasizes clean separation of concerns, with dedicated modules for character management, combat, items, magic, AI, and more.

## Core Patterns & Conventions

### Service Layer Architecture
- **Combat Service** (`game_sys/combat/combat_service.py`) - Centralized combat operations
- **Character Factory** (`game_sys/character/character_factory.py`) - Template-based character creation
- **Config Manager** (`game_sys/config/config_manager.py`) - Thread-safe singleton for JSON configs
- **Item Factory** (`game_sys/items/factory.py`) - Registry-based item creation

### JSON-Driven Configuration
Everything is configurable via JSON files in `game_sys/*/data/`:
- Character templates, jobs, items, spells, enchantments
- Config consolidation in `default_settings.json` with feature toggles
- Use `ConfigManager().get('path.to.setting')` for all config access

### Actor Hierarchy & Stats
```python
# Core character creation pattern
from game_sys.character.character_factory import create_character
player = create_character("hero")  # Uses templates in character_templates.json
enemy = create_character("goblin")

# RPG stats system: primary stats (strength, dexterity, etc.) drive derived stats
# All configurable via multipliers in default_settings.json
```

### Effect & Enchantment System
- **Effect Factory** (`game_sys/effects/factory.py`) - Creates effects from IDs like "fire_damage_10"
- **Equipment Effects** - Automatically applied through ScalingManager
- **Status Effects** - Temporary effects managed by status_manager

## Development Workflows

### Running Tests
```bash
# Comprehensive test suite
python tests/test_comprehensive.py
python tests/run_all_tests.py

# Specific feature tests
python test_improved_critical_hits.py
pytest tests/ --maxfail=1 --disable-warnings -q
```

### Demo Applications
```bash
python demo.py                    # Main tabbed demo (stats, combat, inventory, etc.)
python playground.py              # Engine feature showcase
python tests/test_comprehensive.py # Interactive test manager
```

### Logging System
Always use the integrated logging system:
```python
from game_sys.logging import get_logger
logger = get_logger("module_name")
logger.info("Message")  # Outputs to both console and JSON logs
```

## Advanced Combat System

### Damage Calculation & Resistance
- **DamagePacket System** - Standardized damage with type, source, and modifiers
- **Elemental System** - Fire, ice, lightning, poison, physical damage types
- **Resistance/Weakness** - Multiplicative damage modifiers per element
- **Critical Hit System** - Enhanced crits with healing, variable multipliers

```python
# Combat service usage
from game_sys.combat.combat_service import CombatService
combat_service = CombatService()
result = combat_service.perform_attack(attacker, target, skill_id="power_attack")
```

### Status Effects & DOT/HOT
- **Temporary Effects** - Timed buffs/debuffs with stacking rules
- **Damage Over Time** - Poison, burn effects with tick intervals
- **Healing Over Time** - Regeneration effects
- **Effect Management** - Automatic cleanup and duration tracking

### Combat Hooks & Events
```python
from game_sys.hooks.hooks_setup import emit, on, ON_ATTACK_HIT, ON_SPELL_CAST
# Pre-attack, on-hit, post-attack hooks for modifying combat flow
emit(ON_ATTACK_HIT, attacker=actor, target=enemy, damage=damage_packet)
```

## Magic & Spell System

### Spell Mechanics
- **Resource Costs** - Mana, stamina consumption with cooldowns
- **Cast Times** - Channeling vs instant spells
- **Targeting System** - Single target, AoE shapes (circle, cone, line)
- **Spell Schools** - Elemental, healing, utility categorization

### Combo System
- **Spell Sequences** - Multi-spell combinations with timing windows
- **Combo Bonuses** - Enhanced effects for successful sequences
- **Configuration** - `magic/data/combos.json` defines available combos

```python
# Spell casting
from game_sys.magic.spell_manager import SpellManager
spell_manager = SpellManager()
result = spell_manager.cast_spell(caster, "fireball", targets)
```

### Enchantment System
- **Equipment Enhancement** - Weapons/armor gain magical properties
- **Enchantment Learning** - Level/stat requirements for new enchantments
- **Effect Stacking** - Multiple enchantments with diminishing returns
- **Temporary Enchants** - Time-limited magical enhancements

## Character Progression & Leveling

### Experience & Leveling
```python
# XP gain and level management
if hasattr(player, 'leveling_manager'):
    leveled_up = player.leveling_manager.gain_experience(player, xp_amount)
    if leveled_up:
        available_points = player.leveling_manager.calculate_stat_points_available(player)
```

### Stat Allocation System
- **Base Stats** - strength, dexterity, vitality, intelligence, wisdom, constitution, luck
- **Derived Stats** - attack, defense, health, mana calculated from base stats
- **Stat Points** - Earned per level, allocated manually or via AI
- **Stat Requirements** - Skills/spells gated by minimum stat values

### Job/Class System
- **Job Templates** - Class-based stat bonuses and restrictions
- **Equipment Restrictions** - Class-specific gear limitations
- **Skill Trees** - Job-specific abilities and progression paths

### Skill & Spell Learning
```python
# Learning requirements
skill_requirements = {
    "power_attack": {"level": 2, "strength": 15},
    "berserker_rage": {"level": 5, "strength": 20, "constitution": 15}
}
# Check requirements before learning
if player.level >= req["level"] and player.get_stat("strength") >= req["strength"]:
    player.learn_skill(skill_id)
```

## Data Architecture & Configuration

### JSON Schema Conventions
- **Consistent Structure** - All data files follow standardized patterns
- **Template Inheritance** - Base templates with override capabilities
- **Validation** - Schema validation for config integrity
- **Hot Reloading** - Runtime config updates without restart

### Configuration Hierarchies
```python
# Configuration access patterns
cfg = ConfigManager()
# Feature toggles
if cfg.get('toggles.ai', False):
    # AI system enabled
# Constants with defaults
xp_multiplier = cfg.get('constants.leveling.xp_multiplier', 1.0)
# Nested configuration
combat_settings = cfg.get('combat.damage_calculation', {})
```

### Registry Patterns
- **Factory Registration** - Dynamic loading of items, spells, effects
- **Plugin Architecture** - Modular system components
- **Content Discovery** - Automatic registration from data files

## UI Architecture & Patterns

### Tabbed Interface System
- **Tab Management** - Dynamic tab creation and switching
- **State Isolation** - Each tab manages its own UI state
- **Service Integration** - UI calls business logic, never direct manipulation

### UI Update Patterns
```python
# Proper UI update flow
def update_display(self):
    """Update UI to reflect current game state."""
    if not hasattr(self, 'player') or not self.player:
        return
    
    try:
        # Get current data from game systems
        data = self.game_service.get_display_data()
        
        # Update UI elements
        self.update_ui_elements(data)
        
    except Exception as e:
        logger.error(f"UI update failed: {e}")
        self.show_error_message("Display update failed")
```

### Event Handling & Error Management
- **Graceful Degradation** - UI continues functioning with partial failures
- **User Feedback** - Clear error messages and status updates
- **State Validation** - Check system availability before UI operations

## Testing Strategies & Patterns

### Unit Testing Approach
```python
# Test individual components
def test_combat_damage_calculation():
    attacker = create_test_character("warrior")
    target = create_test_character("goblin")
    damage_packet = combat_service.calculate_damage(attacker, target)
    assert damage_packet.total_damage > 0
```

### Integration Testing
- **System Interactions** - Test component integration points
- **Configuration Testing** - Validate JSON configs and settings
- **UI Testing** - Demo application as integration test platform

### Demo-Driven Testing
- **Interactive Testing** - Use `demo.py` for manual feature validation
- **Regression Testing** - Demo workflows catch integration issues
- **Performance Testing** - Large-scale operations through demo interface

## AI System Integration

### Behavior Trees & Decision Making
- **AI Personalities** - Different behavior patterns per character type
- **Dynamic Difficulty** - AI adapts based on player performance
- **Service Integration** - AI uses same APIs as player actions

```python
# AI decision making
if cfg.get('toggles.ai', False):
    ai_action = ai_manager.get_next_action(character, game_state)
    result = combat_service.execute_action(character, ai_action)
```

### Performance Considerations

### Memory Management
- **Object Pooling** - Reuse frequent objects (damage packets, effects)
- **Weak References** - Prevent circular references in event systems
- **Lazy Loading** - Load content on demand, not at startup

### Optimization Patterns
- **Caching Strategies** - Cache expensive calculations (stat derivations)
- **Batch Operations** - Group similar operations for efficiency
- **Database Queries** - Minimize JSON file reads with smart caching

## Common Implementation Patterns

### Error Handling & Logging
```python
from game_sys.logging import get_logger
logger = get_logger(__name__)

@log_exception  # Automatic error logging decorator
def risky_operation(self):
    try:
        # Implementation
        pass
    except SpecificException as e:
        logger.warning(f"Expected issue: {e}")
        return default_value
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

### Async Operations & Timing
- **TimeManager** - Centralized tick system for time-based operations
- **ActionQueue** - Delayed action execution with priorities
- **Cooldown Management** - Skill/spell cooldown tracking

### State Management Patterns
```python
# Safe state access pattern
def get_character_stat(character, stat_name, default=0):
    """Safely get character stat with fallback."""
    if not hasattr(character, 'get_stat'):
        return default
    
    try:
        return character.get_stat(stat_name)
    except (AttributeError, KeyError):
        logger.warning(f"Stat {stat_name} not found, using default {default}")
        return default
```

## Development Workflows & Best Practices

### Feature Addition Process
1. **Research** - Check `docs/` for architectural guidance
2. **Plan** - Review `instructions/` for implementation patterns  
3. **Implement** - Use `examples/` for code patterns
4. **Configure** - Add feature toggle to `default_settings.json`
5. **Service Layer** - Create service class for business logic
6. **Factory Pattern** - Add factory for object creation if needed
7. **UI Integration** - Update UI to call service methods
8. **Testing** - Add unit tests and demo integration
9. **Documentation** - Update relevant docs and instructions

### Configuration Management
```python
# Adding new configuration
# 1. Add to default_settings.json with feature toggle
{
    "toggles": {
        "new_feature": false
    },
    "new_feature": {
        "setting1": "default_value",
        "nested": {
            "setting2": 100
        }
    }
}

# 2. Access in code with fallbacks
if cfg.get('toggles.new_feature', False):
    setting = cfg.get('new_feature.setting1', 'fallback')
```

### Debugging Techniques
- **Logging Levels** - Use appropriate levels (DEBUG, INFO, WARNING, ERROR)
- **Demo Debugging** - Interactive testing through demo interface  
- **Configuration Inspection** - Runtime config validation and display
- **State Dumping** - Serialize game state for debugging

### Code Organization Standards
- **Modular Structure** - One responsibility per file/class
- **Naming Conventions** - Clear, descriptive names for classes and methods
- **Documentation** - Docstrings for all public methods
- **Type Hints** - Use type annotations for better IDE support

## Integration Guidelines & Patterns

### Service Integration Pattern
```python
# Proper service integration
class NewFeatureService:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = get_logger(self.__class__.__name__)
    
    def perform_action(self, actor, target, **kwargs):
        """Perform feature action with proper error handling."""
        if not self.config.get('toggles.new_feature', False):
            self.logger.warning("New feature is disabled")
            return False
        
        try:
            # Implementation
            result = self._internal_logic(actor, target, **kwargs)
            self.logger.info(f"Action completed: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Action failed: {e}")
            return False
```

### Event System Integration
```python
# Adding new events
from game_sys.hooks.hooks_setup import create_event, emit, on

# Define new event
ON_NEW_ACTION = create_event("on_new_action")

# Emit event
emit(ON_NEW_ACTION, actor=actor, data=action_data)

# Listen for event
@on(ON_NEW_ACTION)
def handle_new_action(actor, data):
    # Handle the event
    pass
```

This architecture supports hot-swappable components, configuration-driven behavior, and clean testing - ideal for iterative RPG development.

## Critical Project-Specific Reminders

- **Always check feature toggles** before implementing optional systems
- **Use service layer** for all business logic, never direct state manipulation
- **Leverage existing factories** for object creation consistency
- **Follow JSON schema patterns** when adding new data structures
- **Test through demo interface** for integration validation
- **Document in appropriate folder** (`docs/`, `instructions/`, or `examples/`)
- **Update configuration** with feature toggles and sensible defaults
