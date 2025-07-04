# Cleanup Instructions

## Removing Unneeded Files

During development, several test and debug files were created. These files are no longer needed and can be safely removed to keep the workspace clean.

To remove these files:

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run the cleanup script:

```bash
python cleanup.py
```

This will remove the following types of files:
- Debug files (debug_*.py)
- Old demo versions
- Deprecated UI demos
- Test files that are no longer needed

The script will create a log file `cleanup.log` with details about which files were removed.

## Currently Needed Files

The main files you should keep:

- `final_game_demo.py` - The main game demo with tabbed UI
- Files in the `ui/` and `rendering/` directories - Core UI and rendering systems
- Files in the `game_sys/` directory - Game engine core
- `logs/` directory - Logging system

All other demo and test files can be safely removed.
