# Enchantment Damage Type Fix

## Issue Description

The enchantment system was setting damage types as strings (e.g., "FIRE", "ICE", "LIGHTNING") instead of using the proper `DamageType` enum values, causing errors when these values were used in combat calculations.

## Root Cause

In the `apply_selected_enchantment` method in `demo.py`, enchantments were being applied with code like:

```python
item.damage_type = "FIRE"  # String value
```

However, in the `__str__` method of the `Weapon` class and elsewhere in the code, the system expected `damage_type` to be a `DamageType` enum value with a `.name` attribute.

## Fix Applied

1. Changed all enchantment application code to use the proper `DamageType` enum values:

```python
from game_sys.core.damage_types import DamageType
item.damage_type = DamageType.FIRE  # Enum value
```

2. Updated the attack method to handle both string values and enum values for `damage_type`:

```python
if isinstance(weapon.damage_type, DamageType):
    damage_type = weapon.damage_type
else:
    # Handle the case where damage_type is a string
    damage_type = getattr(DamageType, weapon.damage_type, DamageType.PHYSICAL)
```

## Related Components

- `demo.py`: Updated enchantment application to use proper enum values
- `game_sys/items/weapon.py`: Expects `damage_type` to be a `DamageType` enum with a `.name` attribute
- `game_sys/core/damage_types.py`: Contains the `DamageType` enum definition

## Testing

After applying these fixes, the user should be able to:
1. Apply enchantments to weapons
2. Use enchanted weapons in combat
3. See proper damage type effects including weaknesses and resistances

The error message "TypeError: attribute name must be string, not 'DamageType'" should no longer appear.
