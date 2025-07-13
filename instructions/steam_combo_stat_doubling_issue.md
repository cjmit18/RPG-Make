# Steam Combo Stat Doubling Issue Investigation

## Problem Description

When the "steam" combo is triggered (fireball + ice_shard sequence), all character stats double and percentage-based stats go into the thousands, creating massive UI display issues and gameplay imbalances.

## Root Cause Analysis

### Issue 1: Double Application of BuffEffect in compute_stat()

**Location**: `game_sys/core/scaling_manager.py:296-315`

**Problem**: The `compute_stat` method applies `BuffEffect` bonuses **twice**:

1. **First application** (lines 296-304): Loops through `actor.active_statuses` and calls `modify_stat()` on all effects
2. **Second application** (lines 307-315): Loops through `actor.stat_bonus_ids` and calls `modify_stat()` again on the same effects

```python
# First application - affects ALL active status effects
for eff_id, (eff, _) in getattr(actor, 'active_statuses', {}).items():
    if hasattr(eff, 'modify_stat'):
        raw = eff.modify_stat(raw, actor)  # BuffEffect applied here

# Second application - affects the SAME BuffEffect again  
for bonus_id in getattr(actor, 'stat_bonus_ids', []):
    if bonus_id in getattr(actor, 'active_statuses', {}):
        eff, _ = actor.active_statuses[bonus_id]
        if hasattr(eff, 'modify_stat'):
            raw = eff.modify_stat(raw, actor)  # BuffEffect applied AGAIN
```

**Result**: A +5 intelligence buff becomes +10 (applied twice).

### Issue 2: Lack of Stat Filtering in BuffEffect

**Location**: `game_sys/effects/extensions.py:89-96`

**Problem**: `BuffEffect.modify_stat()` doesn't check if it should modify the specific stat being computed.

```python
def modify_stat(self, base_stat: float, actor: Any) -> float:
    if self.id in getattr(actor, 'stat_bonus_ids', []):
        new_value = base_stat + self.amount  # No stat_name filtering!
        return new_value
    return base_stat
```

**Expected**: A "intelligence +5" buff should only modify intelligence stats.
**Actual**: The buff modifies **ALL** stats (strength, dexterity, intelligence, etc.).

**Result**: A +5 intelligence buff incorrectly adds +5 to strength, dexterity, constitution, etc.

### Issue 3: Method Signature Inconsistency

**Problem**: Different effect types have inconsistent `modify_stat` signatures:

- **Equipment effects**: `modify_stat(raw, actor, stat_name)` - 3 parameters
- **Status effects**: `modify_stat(raw, actor)` - 2 parameters
- **BuffEffect**: Only accepts 2 parameters, missing `stat_name` filtering

This prevents proper stat-specific filtering in BuffEffect.

## Compound Effect

When both issues combine:
1. Intelligence +5 buff gets applied twice = +10
2. This +10 gets applied to ALL stats (not just intelligence)
3. Final result: ALL stats increase by +10 instead of just intelligence +5

For percentage-based derived stats, this creates exponential growth when the base stats are used as multipliers.

## Steam Combo Configuration

**File**: `game_sys/magic/data/combos.json`

```json
{
  "combos": {
    "steam": {
      "sequence": ["fireball","ice_shard"],
      "effects": [
        { "type":"buff","params":{ "stat":"intelligence","amount":5,"duration":10 } }
      ]
    }
  }
}
```

The combo correctly specifies an intelligence-only buff, but the implementation bugs cause it to affect all stats.

## Solutions Required

### 1. Fix Double Application in ScalingManager

**File**: `game_sys/core/scaling_manager.py`

Remove the duplicate `stat_bonus_ids` loop (lines 307-315) since these effects are already processed in the `active_statuses` loop.

### 2. Add Stat Filtering to BuffEffect

**File**: `game_sys/effects/extensions.py`

Modify `BuffEffect.modify_stat()` to:
- Accept a `stat_name` parameter
- Only apply the buff if `stat_name` matches `self.stat`

```python
def modify_stat(self, base_stat: float, actor: Any, stat_name: str = None) -> float:
    if (self.id in getattr(actor, 'stat_bonus_ids', []) and 
        stat_name == self.stat):  # Only modify the target stat
        new_value = base_stat + self.amount
        return new_value
    return base_stat
```

### 3. Standardize modify_stat Signatures

Ensure all effect types use consistent `modify_stat(base_stat, actor, stat_name)` signature.

## Testing

After fixes, verify:
1. Steam combo only increases intelligence by +5
2. Other stats remain unchanged
3. Percentage-based stats (like critical_chance) stay within normal ranges
4. Multiple combo activations don't stack incorrectly

## Impact Assessment

**Severity**: High - Breaks game balance completely
**Scope**: All BuffEffect-based combinations and status effects
**User Experience**: Makes game unplayable due to stat inflation

This issue affects not just the steam combo, but any system using BuffEffect for temporary stat modifications.