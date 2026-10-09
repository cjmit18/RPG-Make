# Character System Focus Phase

## Current Status: CHARACTER SYSTEM ONLY

This repository is currently in a **Character System Focus Phase**. All other game systems have been temporarily removed to allow for complete implementation and testing of the character system in isolation.

## Active Systems

### ✅ Character System
- **Character Management**: Create, update, delete characters
- **Stat System**: Base stats, derived stats, modifiers
- **Progression System**: Experience, leveling, skill advancement  
- **Inventory System**: Items, equipment, containers

### ✅ Core Engine
- **Event Bus**: Event-driven architecture
- **Service Container**: Dependency injection
- **Async Engine**: Async-first design patterns

### ✅ Integration Service (Mock)
- Provides mock implementations for testing
- No dependencies on removed systems

## Removed Systems

The following systems have been **temporarily removed** and documented for future reimplementation:

- ❌ **Combat System**: Turn-based combat resolution
- ❌ **Quest System**: Quest management and progression  
- ❌ **World System**: Locations, time, world state
- ❌ **UI System**: User interface and input handling

## Architecture Principles

### Complete Decoupling
- Systems communicate **only** through events
- No direct imports between system modules
- Data independence - each system owns its data

### Event-Driven Communication
```python
# ✅ Correct: Event-based communication
await event_bus.publish(CharacterLevelUpEvent(
    character_id="char_123",
    old_level=5,
    new_level=6
))

# ❌ Wrong: Direct system calls
combat_system.update_character_level(character_id, new_level)
```

### Service Container Integration
```python
# ✅ Correct: Dependency injection
class CharacterSystem(AsyncInitializable):
    def __init__(self, service_container: ServiceContainer):
        self.event_bus = None  # Injected during initialization
    
    async def initialize_async(self):
        self.event_bus = await self.service_container.get_service(EventBus)
```

## Development Workflow

### Current Phase: Character System Completion
1. **Complete Character System Features**
   - ✅ Basic character CRUD operations
   - ✅ Stat calculations and modifiers
   - ✅ Experience and leveling mechanics
   - ✅ Inventory and equipment system
   - 🔄 Advanced progression features
   - 🔄 Character relationships and reputation

2. **Comprehensive Testing** 
   - ✅ Unit tests for all character components
   - ✅ Integration tests with event bus
   - 🔄 Performance testing with large datasets
   - 🔄 Save/load functionality testing

### Next Phase: System Reintegration
Once character system is complete:
1. Reimplement combat system with event-driven architecture
2. Add quest system with character integration events
3. Implement world system with location tracking
4. Add UI system with event subscriptions

## Documentation

- 📖 [Module Removal Guide](docs/architecture/MODULE_REMOVAL_GUIDE.md)
- 📖 [Character System Documentation](docs/02-systems/character-system.md)
- 📖 [Event Architecture](docs/01-architecture/event-driven-design.md)
- 📖 [Service Container Usage](docs/01-architecture/dependency-injection.md)

## Quick Start (Character System Only)

```python
from rpg_engine.core.engine import AsyncGameEngine
from rpg_engine.systems.character.character_system import CharacterSystem

# Initialize engine with character system only
engine = AsyncGameEngine()
await engine.initialize_async()

# Get character system
character_system = await engine.service_container.get_service(CharacterSystem)

# Create a character
character_data = {
    'template_id': 'warrior_basic',
    'name': 'Hero',
    'appearance': {'build': 'muscular'}
}
character = await character_system.create_character('player_1', character_data)
```

## Contributing

During this focus phase:
- Focus on character system improvements only
- All changes must maintain event-driven architecture  
- Add comprehensive tests for new features
- Update documentation for character system changes

See [CONTRIBUTING.md](CONTRIBUTING.MD) for detailed guidelines.
