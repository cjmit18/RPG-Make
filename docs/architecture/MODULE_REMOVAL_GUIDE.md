# Module Removal and Reimplementation Guide

## Overview
This document tracks modules that were removed during the character system focus phase and provides guidance for reimplementation.

## Removed Modules (Status: REMOVED)

### Combat System (`rpg_engine/systems/combat/`)
**Purpose**: Combat encounter management and turn-based combat resolution  
**Dependencies**: Character system for participant data  
**Key Interfaces**:
- `CombatSystem.start_combat_async(combat_id, participants)`
- `CombatSystem.execute_action_async(combat_id, actor_id, action_type, target_id)`
- `CombatSystem.get_combat_status_async(combat_id)`

**Events Published**:
- `CombatStartedEvent(combat_id, participants)`
- `CombatEndedEvent(combat_id, winners, losers, duration)`
- `CombatActionEvent(combat_id, actor_id, action_type, target_id, result)`

**Reimplementation Notes**:
- Must use `ServiceContainer` for dependency injection
- Should only interact with character system through events
- Combat participants created from character data, not direct references

### Quest System (`rpg_engine/systems/quest/`)
**Purpose**: Quest management, objective tracking, and reward distribution  
**Dependencies**: Character system for quest progress tracking  
**Key Interfaces**:
- `QuestSystem.start_quest(character_id, quest_id)`
- `QuestSystem.update_objective_progress(character_id, objective_type, progress)`
- `QuestSystem.complete_quest(character_id, quest_id)`

**Events Published**:
- `QuestStartedEvent(quest_id, character_id, quest_name)`
- `QuestCompletedEvent(quest_id, character_id, quest_name, rewards)`
- `ObjectiveCompletedEvent(quest_id, objective_id, character_id)`

**Reimplementation Notes**:
- Quest progress should be stored independently of character system
- Character rewards applied through character system events
- Support for dynamic quest generation

### World System (`rpg_engine/systems/world/`)
**Purpose**: World state management, locations, and time systems  
**Dependencies**: None (independent world state)  
**Key Interfaces**:
- `WorldSystem.get_location(location_id)`
- `LocationSystem.move_character(character_id, from_location, to_location)`
- `TimeSystem.advance_time(duration)`

**Events Published**:
- `LocationChangedEvent(character_id, old_location, new_location)`
- `TimeAdvancedEvent(old_time, new_time, duration)`

**Reimplementation Notes**:
- World state should be completely independent
- Character location tracking through events only
- Time system affects all other systems through events

### UI System (`rpg_engine/systems/ui/`)
**Purpose**: User interface management and input handling  
**Dependencies**: All systems for display data  
**Key Interfaces**:
- `InputSystem.register_handler(input_type, handler)`
- `LayoutSystem.render_ui(screen_data)`
- `AnimationSystem.play_animation(animation_id, target)`

**Events Published**:
- `InputReceivedEvent(input_type, input_data)`
- `UIUpdatedEvent(ui_element_id, new_state)`

**Reimplementation Notes**:
- Should be completely event-driven
- No direct system dependencies
- Subscribes to events from all systems for display updates

### Integration Service (`rpg_engine/systems/integration/`)
**Purpose**: System coordination and cross-system communication  
**Status**: MODIFIED - Only mock character data methods remain  
**Remaining Interfaces**:
- `get_character_data_async(character_id)` - Returns mock data
- `get_available_character_templates_async()` - Returns mock templates
- `get_system_statistics_async()` - Returns mock statistics

**Reimplementation Notes**:
- Should coordinate between all systems through events
- No direct system references
- Acts as orchestrator for complex multi-system operations

## Character System (Status: RETAINED)

### Core Components
- `CharacterSystem`: Main character management
- `StatSystem`: Stat calculations and modifiers  
- `ProgressionSystem`: Experience and leveling
- `InventorySystem`: Item and equipment management

### Event Architecture
All character operations publish events:
- Character lifecycle: `CharacterCreatedEvent`, `CharacterDeletedEvent`
- Progression: `CharacterLevelUpEvent`, `ExperienceGainedEvent`, `SkillLearnedEvent`
- Stats: `StatChangedEvent`, `DerivedStatsCalculatedEvent`
- Inventory: `ItemAddedEvent`, `ItemRemovedEvent`, `EquipmentChangedEvent`

## Decoupling Guidelines

### Event-Driven Communication
- Systems MUST NOT import other system modules directly
- All inter-system communication through `EventBus`
- Systems subscribe to events they need to handle
- Systems publish events for state changes

### Service Container Usage
- All systems registered in `ServiceContainer`
- Dependencies injected through container
- Engine manages system lifecycle through container

### Data Independence
- Each system maintains its own data store
- No shared data structures between systems
- Character data accessed only through character system events

## Reimplementation Checklist

When adding systems back:

1. **Event Interface Design**
   - [ ] Define all events the system publishes
   - [ ] Define all events the system subscribes to
   - [ ] Ensure events contain all necessary data

2. **Service Registration**
   - [ ] Implement `AsyncInitializable` interface
   - [ ] Register system in engine initialization
   - [ ] Inject dependencies through `ServiceContainer`

3. **Decoupling Validation**
   - [ ] No direct imports of other system modules
   - [ ] No shared data structures
   - [ ] All communication through events

4. **Testing**
   - [ ] Unit tests for system functionality
   - [ ] Integration tests for event communication
   - [ ] Mock other systems in tests

## Migration Scripts

See `scripts/module_cleanup.py` for automated removal process.
See `scripts/system_validator.py` for decoupling validation.
