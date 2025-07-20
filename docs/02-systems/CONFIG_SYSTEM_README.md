# Configuration System Update

The configuration system has been updated to consolidate settings into a single file: `default_settings.json`.

## Changes

1. **Consolidated Configuration File**:
   - All settings from `game_settings.json` have been merged into `default_settings.json`.
   - This includes leveling, skills, spells, enchantments, and UI configuration.

2. **Backward Compatibility**:
   - For backward compatibility, the system will look for `game_settings.json` if `default_settings.json` doesn't exist.
   - This ensures existing code will continue to work during the transition.

3. **Configuration Hierarchy**:
   - `default_settings.json`: Primary configuration file with all game settings
   - `settings.json`: User-specific overrides (optional)

4. **ConfigManager Improvements**:
   - Added a `get_section()` method to easily access entire configuration sections
   - Enhanced validation to include new configuration sections

## Usage

To access configuration values, continue to use the ConfigManager as before:

```python
from game_sys.config.config_manager import ConfigManager

# Get the singleton instance
config = ConfigManager()

# Access a specific value with dot notation
max_level = config.get('constants.leveling.max_level', 100)  # Default is 100

# Access an entire section
skills = config.get_section('skills', {})
spells = config.get_section('spells', {})
```

## Migration

The `game_settings.json` file is no longer needed and can be removed once all code has been updated to use `default_settings.json`.

If you have custom modifications in `game_settings.json`, they should be moved to either:
- `default_settings.json` for default values
- `settings.json` for user-specific overrides

## Schema

The configuration schema now includes these top-level sections:
- toggles
- modules
- constants
- defaults
- randomness
- logging
- paths
- leveling
- skills
- spells
- enchantments
- ui
