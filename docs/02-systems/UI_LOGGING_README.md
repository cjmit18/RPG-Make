# UI System and Logging Integration

## Overview

This project has been enhanced with a UI system and integrated logging throughout the engine.

## Main Demo

The `final_game_demo.py` provides a simple demonstration of the game engine with:

- Character creation and combat
- UI interaction via Tkinter
- Visual effects with particles
- Integrated logging system

To run the demo:

```bash
python final_game_demo.py
```

## Architecture

The system now includes:

- **Core Game Engine**: Character systems, combat, items, and effects
- **UI Components**: Simple but effective UI using Tkinter
- **Logging System**: Comprehensive logging with file and console output

## Logging System

The logging system (in the `logs/` folder) provides:

- Console output with configurable levels
- File-based logging in both text and JSON formats
- Centralized setup and configuration

To use the logging system in your code:

```python
from logs.logs import get_logger, setup_logging

# Initialize logging
setup_logging()

# Get a logger for your module
logger = get_logger("my_module")

# Use the logger
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")
```

## Dependencies

The project requires:
- Python 3.6+
- Tkinter (standard library)
- watchdog (for config file watching)

All dependencies are listed in requirements.txt.
