# RPG Engine Start Menu System Documentation

## Overview

The Start Menu System provides a comprehensive main menu interface for RPG games built with the RPG Engine's async-sync bridge. The engine includes an `AsyncUIManager` that properly bridges tkinter's synchronous nature with the async engine architecture.

## Key Architecture Feature: Async-Sync Bridge

The RPG Engine includes a built-in **AsyncUIManager** that solves the async/sync problem:

```python
class AsyncUIManager(AsyncInitializable, AsyncShutdownable):
    """
    Manages the UI system with async support
    Bridges tkinter's synchronous nature with our async engine
    """
```

This bridge:
- **Runs tkinter in a separate thread** - Prevents blocking the async event loop
- **Provides async communication** - Uses `asyncio.Queue` for thread-safe communication  
- **Handles event integration** - Connects with the EventBus system
- **Manages lifecycle** - Proper initialization and shutdown

## Architecture

### Core Components

#### StartMenuManager (Recommended)
```python
class StartMenuManager:
    """Start menu using the async-sync bridge"""
    
    def __init__(self, service_container: ServiceContainer)
    async def initialize() -> None  # Uses AsyncUIManager bridge
    def create_main_menu() -> UIDefinition
    async def show_menu() -> None
```

### Service Dependencies
- **ServiceContainer** - Dependency injection and service management
- **ModularUIManager** - UI creation and widget management (non-async setup)
- **EventBus** - Event-driven communication (optional)

## Usage Examples

### Basic Start Menu
```python
import asyncio
from rpg_engine.ui.start_menu import StartMenuManager
from rpg_engine.ui.modular_ui_system import ModularUIManager
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus

async def run_basic_menu():
    # Setup services
    service_container = ServiceContainer()
    service_container.register_singleton(EventBus, lambda c: EventBus())
    service_container.register_singleton(ModularUIManager, lambda c: ModularUIManager(c))
    
    # Create menu
    start_menu = StartMenuManager(service_container)
    await start_menu.initialize()
    
    # Run menu
    start_menu.run_menu()

# Run the menu
asyncio.run(run_basic_menu())
```

### Enhanced Menu with Custom Callbacks
```python
from examples.enhanced_start_menu import EnhancedStartMenu

async def run_enhanced_menu():
    # Setup services (same as above)
    service_container = ServiceContainer()
    service_container.register_singleton(EventBus, lambda c: EventBus())
    service_container.register_singleton(ModularUIManager, lambda c: ModularUIManager(c))
    
    # Create enhanced menu
    menu = EnhancedStartMenu(service_container)
    await menu.initialize()
    
    # Customize settings
    menu.game_title = "🏰 My RPG Game"
    menu.version = "v1.0 Beta"
    
    # Run menu
    menu.run_menu()

asyncio.run(run_enhanced_menu())
```

### Integration with Game Engine
```python
from rpg_engine.core.engine import AsyncGameEngine

class RPGGame:
    def __init__(self):
        self.engine = AsyncGameEngine()
        self.start_menu = None
    
    async def start(self):
        # Initialize engine
        await self.engine.initialize()
        
        # Create start menu
        self.start_menu = StartMenuManager(self.engine.service_container)
        await self.start_menu.initialize()
        
        # Set up callbacks
        self.start_menu.on_new_game = self.handle_new_game
        self.start_menu.on_load_game = self.handle_load_game
        self.start_menu.on_exit = self.handle_exit
        
        # Show menu
        self.start_menu.run_menu()
    
    def handle_new_game(self):
        """Start new game logic"""
        self.start_menu.close_menu()
        # Initialize game world, player, etc.
    
    def handle_load_game(self):
        """Load existing game logic"""
        # Show load dialog, restore game state
        pass
    
    def handle_exit(self):
        """Clean shutdown logic"""
        self.start_menu.close_menu()
        asyncio.get_event_loop().stop()

# Start the game
game = RPGGame()
asyncio.run(game.start())
```

## Customization

### Menu Appearance
```python
# Customize game branding
menu.game_title = "🏰 Castle Quest RPG"
menu.version = "v2.1 - Dragon Edition"

# Custom window sizing
main_menu = menu.create_main_menu()
main_menu.geometry = "1200x800"  # Larger window
main_menu.style_theme = "darkly"  # Different theme
```

### Button Actions
```python
# Override default handlers
def custom_new_game(self):
    """Custom new game logic"""
    # Show custom character creation screen
    # Initialize game with specific settings
    # Skip default dialog
    pass

# Replace handler
menu.handle_new_game = custom_new_game
```

### Settings Configuration  
```python
# Extend settings
menu.settings.update({
    'combat_speed': 'Normal',
    'auto_equip': True,
    'show_damage_numbers': True,
    'ui_scale': 1.0
})

# Custom settings dialog
def create_custom_settings(self):
    return UIBuilder("Game Configuration") \
        .add_label("Combat Settings") \
        .add_combobox(values=["Slow", "Normal", "Fast"], variable="combat_speed") \
        .add_checkbutton("Auto-equip better items", variable="auto_equip") \
        # ... more settings
        .build()

menu.create_settings_dialog = create_custom_settings
```

## Event Integration

### Menu Events
```python
from rpg_engine.core.event_bus import EventBus

# Listen for menu events
@event_bus.subscribe
def on_menu_action(event):
    if event.action == "new_game":
        logger.info(f"New game started with character: {event.character_name}")
    elif event.action == "settings_changed":
        logger.info(f"Settings updated: {event.settings}")

# Menu emits events automatically
menu.run_menu()  # Will emit events when buttons are clicked
```

### Custom Events
```python
# Emit custom events from menu handlers
def handle_new_game(self):
    # Create character
    character_data = self.get_character_creation_data()
    
    # Emit event
    self.event_bus.publish(GameEvent(
        type="character_created",
        character=character_data,
        timestamp=time.time()
    ))
    
    # Continue with game start
    self.start_game(character_data)
```

## File Organization

```
rpg_engine/ui/
├── start_menu.py              # Basic StartMenuManager class
├── modular_ui_system.py       # UI framework
└── ui_builder.py              # Fluent UI builder APIs

examples/
├── start_menu_demo.py         # Basic demo
├── enhanced_start_menu.py     # Feature-rich demo
└── game_integration_demo.py   # Full game integration

docs/
└── START_MENU_SYSTEM.md       # This documentation
```

## Best Practices

### 1. Service Initialization
Always initialize services properly:
```python
# ✅ Correct
service_container.register_singleton(ModularUIManager, lambda c: ModularUIManager(c))

# ❌ Incorrect  
service_container.register_singleton(ModularUIManager, ModularUIManager)
```

### 2. Error Handling
Wrap menu operations in try-catch blocks:
```python
def handle_menu_action(self):
    try:
        # Menu logic here
        result = self.perform_action()
        if not result.success:
            messagebox.showerror("Error", result.error)
    except Exception as e:
        logger.error(f"Menu action failed: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
```

### 3. Resource Management
Clean up resources properly:
```python
def close_menu(self):
    """Clean shutdown"""
    if self.current_app:
        self.current_app.destroy()
        self.current_app = None
    
    if hasattr(self, 'background_music'):
        self.background_music.stop()
```

### 4. Configuration Persistence
Save settings between sessions:
```python
import json
from pathlib import Path

def save_settings(self):
    """Save settings to file"""
    settings_file = Path("config/menu_settings.json")
    settings_file.parent.mkdir(exist_ok=True)
    
    with open(settings_file, 'w') as f:
        json.dump(self.settings, f, indent=2)

def load_settings(self):
    """Load settings from file"""
    settings_file = Path("config/menu_settings.json") 
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            self.settings.update(json.load(f))
```

## Troubleshooting

### Common Issues

#### 1. Service Registration Errors
```
TypeError: ModularUIManager.__init__() missing 1 required positional argument: 'service_container'
```
**Solution**: Use lambda in service registration:
```python
service_container.register_singleton(ModularUIManager, lambda c: ModularUIManager(c))
```

#### 2. Widget Option Errors
```
_tkinter.TclError: unknown option "-font"
```
**Solution**: TTK widgets don't support all Tkinter options. Use styling instead:
```python
# ❌ Don't do this
.add_button("Text", font=('Arial', 12))

# ✅ Do this instead  
.add_button("Text")  # Use default styling
```

#### 3. Dialog Not Showing
**Solution**: Ensure UI manager is initialized:
```python
await start_menu.initialize()  # Must call before creating dialogs
```

#### 4. Menu Crashes on Button Click
**Solution**: Check command handlers are properly bound:
```python
.with_command("button_name", self.handler_method)  # Method reference, not call
```

## Advanced Features

### Custom Widgets
```python
from rpg_engine.ui.custom_widgets import register_game_widgets

# Register custom widgets
register_game_widgets(ui_manager)

# Use in menu
.add_widget("character_preview", character_data=character)
.add_widget("save_game_list", save_directory="saves/")
```

### Theming
```python
# Apply custom themes
.with_theme("darkly")    # Dark theme
.with_theme("superhero") # Hero theme  
.with_theme("vapor")     # Retro theme
```

### Animations
```python
def animate_menu_entrance(self):
    """Animate menu appearance"""
    # Fade in effect
    self.current_app.root.attributes('-alpha', 0.0)
    self.fade_in(self.current_app.root)

def fade_in(self, widget, alpha=0.0):
    """Fade in animation"""
    if alpha < 1.0:
        widget.attributes('-alpha', alpha)
        widget.after(50, lambda: self.fade_in(widget, alpha + 0.1))
```

## Performance Considerations

- **Lazy Loading**: Create dialogs only when needed
- **Resource Cleanup**: Destroy unused windows
- **Event Unbinding**: Remove event handlers when closing
- **Memory Management**: Clear large data structures

## Summary

The Start Menu System provides a robust, customizable foundation for RPG game menus. It leverages the modular UI system to create professional-looking interfaces with minimal code while maintaining flexibility for customization and extension.

Key benefits:
- **Declarative UI Definition** - Easy to read and modify
- **Service Integration** - Clean dependency management  
- **Event-Driven Architecture** - Loose coupling between components
- **Extensible Design** - Easy to add new features and dialogs
- **Error Handling** - Robust error management and user feedback
