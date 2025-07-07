# Resistance, Requirements, and Loot System Refactoring

## Summary of Changes

This update addresses three major architectural improvements to the game system:

1. **Resistance/Weakness System Fix**: 
   - Fixed the issue where changing enemy weaknesses or multipliers in JSON files did not affect actual damage calculation
   - Now enemy resistances and weaknesses are properly loaded from JSON template files
   - Removed hardcoded resistances/weaknesses from demo.py
   - Added proper display of resistances/weaknesses in the UI and combat log

2. **JSON-Only Requirements and Availability**:
   - Moved all requirements for enchantments to JSON files
   - Requirements (level, stats) are now defined only in JSON, not hardcoded in Python
   - Ensures that all requirement changes can be made without touching code

3. **JSON-Based Loot System**:
   - Refactored loot table system to use a JSON file for per-entity loot data
   - Created a new loot_tables.json file with enemy-specific loot tables
   - Items now dynamically receive appropriate level, grade, and rarity based on the enemy killed
   - Added guaranteed and possible item lists per enemy type
   - Improved randomization and player luck integration

## Benefits

1. **Maintainability**: Game designers can modify game balance without touching code
2. **Flexibility**: Enemy types have unique loot tables with appropriate rewards
3. **Consistency**: All game data is stored in a uniform way in JSON files
4. **Scalability**: Easy to add new enemies with their own weakness/resistance profiles and loot tables

## Usage

### Resistances and Weaknesses

Resistances and weaknesses are defined in `character_templates.json` like this:

```json
{
  "dragon": {
    "weakness": {"ICE": 0.5},
    "resistance": {"FIRE": 0.75, "PHYSICAL": 0.25}
  }
}
```

Values represent multipliers: 
- For weaknesses, damage is increased by the multiplier (e.g., 0.5 means 50% more damage)
- For resistances, damage is reduced by the multiplier (e.g., 0.75 means 75% damage reduction)

### Requirements

Requirements are defined in the JSON files for each enchantment/spell/skill:

```json
{
  "fire_enchant": {
    "level_requirement": 3,
    "stat_requirements": {
      "intelligence": 12
    }
  }
}
```

### Loot Tables

Loot tables are defined in `loot_tables.json` with the following structure:

```json
{
  "dragon": {
    "default_item_level": 20,
    "grade_chances": { ... },
    "rarity_chances": { ... },
    "possible_items": [ ... ],
    "guaranteed_items": [ ... ],
    "gold_range": [100, 500],
    "exp_multiplier": 3.0
  }
}
```

Each enemy type has its own loot table, with appropriate chances for different item grades and rarities.
