# Game Engine Demo

This project is a demonstration of a game engine with integrated UI, rendering, and logging systems.

## Features

- **Game Engine** - Core game mechanics, combat system, character management, items, and effects
- **UI System** - Modular UI system with widgets, layouts, themes, and animations
- **Rendering System** - Flexible rendering pipeline for game visuals
- **Logging System** - Comprehensive logging throughout all components

## Demo Application

The main demo application is `unified_game_demo.py`, which demonstrates all the systems working together.

### Running the Demo

```bash
python unified_game_demo.py
```

### Controls

- **Spawn Character** - Creates a new random enemy character
- **Attack** - Attacks the current enemy
- **Heal** - Heals the player character
- **Create Item** - Creates a random item and adds it to the player's inventory
- **Add Effect** - Adds a random effect to the player
- **Quit** - Exits the demo

## System Architecture

### UI System

The UI system consists of:

- `UIManager` - Manages all UI components and their interactions
- `BaseWidget` - Base class for all UI widgets
- `Basic Widgets` - Button, Label, Panel, etc.
- `Game Widgets` - Game-specific widgets like CharacterPanel, GameLogPanel
- `Layout System` - BoxLayout, GridLayout, etc.
- `Theme System` - Customizable visual styles
- `Animation System` - UI animations

### Rendering System

The rendering system provides:

- `Renderer` - Main rendering interface
- `TkRenderer` - Tkinter-based implementation
- `RenderPipeline` - Processes render commands
- `RenderTypes` - Type definitions for rendering

### Logging System

The logging system features:

- Console output with configurable levels
- File-based logging (text and JSON formats)
- Integration throughout all components
- Custom formatters and handlers

## Integration

All systems are designed to work together seamlessly. The logging system is integrated throughout the engine to provide visibility into the application's operation.

## Requirements

- Python 3.6+
- Tkinter (included in standard Python installation)
- watchdog (for config file watching)

## Development

See `CONTRIBUTING.md` for development guidelines.
