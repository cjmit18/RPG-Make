# Loot System Refactoring

## Overview

The loot system has been refactored to use the grades and rarities defined in the game's configuration system.
This ensures consistency across the codebase and allows for easier modification of the loot system through JSON configuration files.

## Changes Made

### 1. Updated `LootTable` Class

- Now uses `ConfigManager` to retrieve grade and rarity values from the configuration
- Loads grade and rarity weights from the configuration instead of hardcoding them
- Uses consistent naming conventions for grades and rarities

### 2. Updated Loot Tables JSON

- Updated `grade_chances` to use the standard grade values from the config (`ONE` through `SEVEN`)
- Updated `rarity_chances` to use the standard rarity values from the config (`COMMON`, `UNCOMMON`, `RARE`, etc.)
- Adjusted the drop chances for each enemy type to better match their difficulty level

### 3. Benefits of Changes

- Consistent naming and values throughout the codebase
- All loot-related settings are now configurable through JSON files
- Easier to update and maintain
- More flexibility in defining custom loot tables per enemy type

## Config Values Used

- `defaults.grades`: The list of possible item grades
- `defaults.rarities`: The list of possible item rarities
- `randomness.rarity_weights`: The default drop chances for each rarity
- `randomness.grade_weights`: The default drop chances for each grade

## How to Use

The loot system now dynamically assigns item level, grade, and rarity based on the enemy killed.
To customize loot for a specific enemy type, edit the corresponding entry in `game_sys/loot/data/loot_tables.json`.

Each enemy can have custom:

- Default item level
- Grade probabilities
- Rarity probabilities
- Possible and guaranteed item drops
- Gold range
- Experience multiplier

If an enemy type is not found in the loot tables, it falls back to the `default` table.
