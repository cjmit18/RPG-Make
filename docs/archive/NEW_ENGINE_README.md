# RPG Engine v2.0 - Async-First Architecture

A modern, async-first RPG game engine built from scratch with interactive UI and event-driven architecture.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Engine**
   ```bash
   python main.py
   ```

3. **Run Tests**
   ```bash
   python test_engine.py
   # or
   pytest test_engine.py
   ```

## 🏗️ Architecture Overview

### Core Components

- **`AsyncGameEngine`** - Main engine orchestrator with async game loop
- **`ServiceContainer`** - Dependency injection with async initialization 
- **`EventBus`** - Strongly-typed event system with middleware support
- **`AsyncUIManager`** - Interactive UI system with tkinter integration

### Key Features

- ✅ **Async-First Design** - Built around async/await patterns
- ✅ **Dependency Injection** - Clean service management and lifecycle
- ✅ **Event-Driven Architecture** - Strongly-typed events with middleware
- ✅ **Interactive UI** - Real-time engine controls and monitoring
- ✅ **Modern Patterns** - Service-oriented architecture with clean separation

## 📁 Project Structure

```
rpg_engine/
├── core/
│   ├── engine.py           # Main async game engine
│   ├── service_container.py # Dependency injection container
│   └── event_bus.py        # Event system with strong typing
├── ui/
│   └── ui_system.py        # Async UI management
└── __init__.py

main.py                     # Application entry point
test_engine.py             # Test suite
config.json               # Engine configuration
requirements.txt          # Dependencies
```

## 🎮 Using the Interactive UI

The UI provides real-time interaction with the engine:

### Engine Controls
- **Start Engine** - Initialize and start the async game loop
- **Pause Engine** - Pause engine execution
- **Stop Engine** - Stop the engine gracefully

### Monitoring
- **Engine Status** - Real-time engine state, FPS, frame count
- **Event Statistics** - Published/handled events, error counts
- **Service Information** - Registered services and their status

### Testing
- **Test Event** - Trigger test events to verify event bus
- **Clear Log** - Clear the output log

## 🔧 Configuration

Edit `config.json` to customize:

- Engine settings (FPS, debug mode)
- UI appearance (window size, theme)
- Logging configuration
- Service options

## 🧪 Testing

The engine includes comprehensive tests:

```bash
# Run manual test
python test_engine.py

# Run with pytest (if installed)
pytest test_engine.py -v

# Run async tests
pytest test_engine.py::test_engine_initialization -v
```

## 🎯 Next Steps

This foundation supports the implementation of:

1. **Game Systems** - Character, combat, inventory systems
2. **Resource Management** - Asset loading and caching
3. **Plugin Architecture** - Dynamic plugin loading
4. **Networking** - Multiplayer foundation
5. **Advanced UI** - Game-specific UI components

## 🔍 Development Notes

### Adding New Services

```python
from rpg_engine.core.service_container import AsyncInitializable

class MyService(AsyncInitializable):
    async def initialize_async(self) -> None:
        # Async initialization logic
        pass

# Register in engine initialization
container.register_singleton(MyService, MyService)
```

### Creating Custom Events

```python
from rpg_engine.core.event_bus import GameEvent
from dataclasses import dataclass

@dataclass(frozen=True)
class CustomEvent(GameEvent):
    custom_data: str
    value: int

# Publish events
await event_bus.publish(CustomEvent(
    timestamp=0,  # Auto-filled
    source="my_system",
    custom_data="test",
    value=42
))
```

### Adding UI Components

```python
from rpg_engine.ui.ui_system import UIComponent

class MyUIComponent(UIComponent):
    def create_widget(self, parent_widget):
        # Create tkinter widgets
        return my_widget
    
    async def update_async(self, data):
        # Handle async updates
        pass
```

## 📝 License

This project follows the same license as the original RPG Engine project.

---

*Built with modern async patterns for scalable game development*
