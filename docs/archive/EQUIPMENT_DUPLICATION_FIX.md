# Equipment Duplication Bug Fix

## Problem
Items were duplicating stats when being equipped/unequipped in the demo system. This was causing stat values to accumulate incorrectly.

## Root Cause
The issue was caused by **dual stat application**:

1. **Manual stat manipulation** in demo.py was directly modifying `actor.base_stats` when equipping/unequipping items
2. **Automatic effect system** was also applying item effects through the new comprehensive effect system via `scaling_manager.py`

This resulted in the same stat bonus being applied twice.

## Solution

### 1. Fixed demo.py Equipment Logic

**Before:**
```python
# Apply armor stats if available
if hasattr(item, 'stats'):
    for stat_name, bonus in item.stats.items():
        current_val = self.player.base_stats.get(stat_name, 0.0)
        new_val = current_val + bonus
        self.player.base_stats[stat_name] = new_val
```

**After:**
```python
# NOTE: Do NOT manually apply stats here - the new effect system
# handles item effects automatically through the scaling manager
# when effect_ids are present on items
```

### 2. Fixed scaling_manager.py Effect Application

**Before:**
```python
raw = effect.modify_stat(raw, actor)  # Missing stat_name parameter
```

**After:**
```python
raw = effect.modify_stat(raw, actor, stat_name)  # Correct parameters
```

### 3. Added Effect Type Filtering

**Before:**
```python
if hasattr(effect, 'modify_stat'):
    # Applied to ALL effects with modify_stat method
```

**After:**
```python
if (hasattr(effect, 'modify_stat') and hasattr(effect, 'stat_name')):
    # Only applied to stat-modifying effects like EquipmentStatEffect
    # Skips regeneration effects that work via tick() method
```

## Results

✅ **No More Duplication**: Stats return to exact original values after unequipping
✅ **Proper Effect Application**: Equipment effects (like spell_power_10) are correctly applied
✅ **No Errors**: Regeneration effects are properly ignored for stat calculation
✅ **Automatic Integration**: Works seamlessly with the new comprehensive effect system

## Test Results

```
Initial stats:
  Derived Spell Power: 0.0

After equipping Archmage Robes:
  Derived Spell Power: 10.0  (+10.0 bonus from spell_power_10 effect)

After unequipping:
  Derived Spell Power: 0.0   (returns to original value)

✅ SUCCESS: No stat duplication detected!
```

## Files Modified

- `demo.py`: Removed manual stat manipulation in equipment methods
- `game_sys/core/scaling_manager.py`: Fixed effect parameter passing and added filtering

The equipment system now works correctly with the comprehensive effect system without any duplication issues!
