# Test Suite Documentation

This directory contains the consolidated test suite for the game system. The tests have been organized and redundant files removed.

## Core Test Files

### `test_core_functionality.py`
Tests fundamental game mechanics:
- Character creation and basic stats
- Job system and equipment assignment
- Basic combat mechanics
- Health restoration

### `test_combat_comprehensive.py`
Comprehensive combat system tests:
- Damage calculation with various modifiers
- Combat capabilities testing
- Edge cases and error conditions
- Stat integration in combat

### `test_integration.py`
Integration tests for system interactions:
- Equipment system integration
- Job assignment with equipment
- Combat system integration
- Resource management

### `conftest.py`
Shared test fixtures and configuration:
- Deterministic RNG for testing
- Player and enemy factory functions
- Clean test environments
- Sample items and equipment

## Specialized Test Files

### `test_actor.py`
Tests for the Actor class and character properties.

### `test_inventory.py`
Tests for inventory management and item handling.

### `test_two_handed.py`
Tests for two-handed weapon restrictions and mechanics.

### `test_jobs.py`
Tests for job assignment and job-specific mechanics.

### `test_items.py`
Tests for item creation, properties, and behavior.

### `test_skills.py`
Tests for skill systems and passive abilities.

### `test_mage.py`
Tests specific to mage class mechanics.

### `test_buffs.py`
Tests for buff/debuff systems.

### `test_hooks.py`
Tests for the event hook system.

### `test_loot.py`
Tests for loot generation and distribution.

### `test_stamina.py`
Tests for stamina resource management.

### `test_dual_wield.py`
Tests for dual wielding mechanics.

### `test_block_chance.py`
Tests for blocking mechanics and probability.

### `test_basic_properties.py`
Tests for basic character properties and attributes.

### `test_simple.py`
Simple smoke tests for basic functionality.

### `test_final.py`
Final verification tests for resource drain systems.

## Removed Files

The following redundant or unnecessary files were removed:
- `test_comprehensive.py` (empty)
- `test_two_handed.py` (empty, replaced with populated version)
- `debug_drain.py` (debug utility)
- `quick_test.py` (simple utility)
- `simple_test.py` (basic import test)
- `test_combat_simple.py` (redundant)
- `test_combat_new.py` (consolidated into comprehensive)
- `test_combat.py` (redundant)
- `test_combat_refactor.py` (redundant)
- `test_combat_complete.py` (redundant)
- `test_combat_damage_calc.py` (redundant)
- `test_inventory.py` (replaced with newer version)
- `test_micropatches.py` (temporary)
- `test_minor_patches.py` (temporary)
- `test_refinements.py` (temporary)
- `demonstrate_complete_polish.py` (demo file)
- `test_suite_refactor_demo.py` (demo file)
- `test_comprehensive_final.py` (broken/incomplete)
- `test_collision_performance.py` (performance test)
- `test_damage_packet_and_profiler.py` (profiling test)
- `test_learning.py` (specialized test)
- `test_all_drains.py` (duplicate)
- `test_drain.py` (duplicate)

## Running Tests

To run the entire test suite:
```bash
pytest tests/
```

To run specific test categories:
```bash
# Core functionality
pytest tests/test_core_functionality.py

# Combat system
pytest tests/test_combat_comprehensive.py

# Integration tests
pytest tests/test_integration.py
```

To run with verbose output:
```bash
pytest tests/ -v
```

## Test Organization Principles

1. **Consolidation**: Related tests are grouped together
2. **Clarity**: Test names clearly indicate what is being tested
3. **Maintainability**: Shared fixtures reduce code duplication
4. **Coverage**: Core functionality is thoroughly tested
5. **Integration**: System interactions are tested together
