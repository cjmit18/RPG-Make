# Dual Wield Implementation Guide

## Current Issue Analysis

### Problem Description
When a dagger is equipped in the offhand slot and attempting to equip a second iron dagger in the weapon slot, the operation fails. This happens due to conflicting dual wield logic between different parts of the system.

### Root Cause
The issue stems from inconsistent slot definitions and dual wield logic:

1. **Slot Configuration Conflict**:
   - `iron_dagger` in `items.json` has `"slot": "offhand"` and `"slot_restriction": "either_hand"`
   - This creates confusion: should it go in offhand (slot) or either (restriction)?

2. **Demo Logic Issue**:
   - The demo's `equip_selected_item()` function at lines 2170-2172 checks for dual wield compatibility
   - But it only allows weapon→offhand movement, not offhand→weapon swapping

3. **Actor Logic Mismatch**:
   - `actor.py` has `equip_weapon_smart()` method designed for this case
   - But the demo doesn't use the smart equipping method

## Technical Analysis

### Current Dual Wield Flow
```
1. User has dagger in offhand (slot="offhand", dual_wield=true)
2. User tries to equip iron_dagger in weapon slot
3. Demo checks: item.dual_wield=true AND current_weapon.dual_wield=true
4. Since current_weapon=None (dagger is in offhand), dual_wield check fails
5. Equipment fails with "Weapon slot occupied" error
```

### Item Configuration Analysis
From `items.json`:
```json
"iron_dagger": {
  "slot": "offhand",           // Forces offhand placement
  "slot_restriction": "either_hand",  // But allows either hand
  "dual_wield": true           // Supports dual wielding
}
```

## Solution Approaches

### Option 1: Fix Demo Logic (Recommended)
Modify the demo's equipment logic to handle reverse dual wield scenario:

```python
# In demo.py equip_selected_item() around line 2170
if slot == 'weapon':
    current_weapon = getattr(self.player, 'weapon', None)
    current_offhand = getattr(self.player, 'offhand', None)
    
    if current_weapon is None:
        # Check if we can move offhand to weapon for dual wield
        if (current_offhand is not None and 
            hasattr(item, 'dual_wield') and item.dual_wield and
            hasattr(current_offhand, 'dual_wield') and current_offhand.dual_wield):
            # Move offhand to weapon slot, new item goes to weapon
            slot_available = True
        else:
            slot_available = True
```

### Option 2: Use Smart Equipping
Replace direct equip calls with the smart equipping method:

```python
# Instead of self.player.equip_weapon(item)
success = self.player.equip_weapon_smart(item)
```

### Option 3: Fix Item Configuration
Standardize dual wield items to have consistent slot definitions:

```json
"iron_dagger": {
  "slot": "weapon",            // Primary slot
  "slot_restriction": "either_hand",
  "dual_wield": true
}
```

## Implementation Plan

### Phase 1: Quick Fix (Demo Logic)
1. Modify `demo.py` equipment validation to check both directions
2. Add logic to swap offhand→weapon when appropriate
3. Test with existing dagger configurations

### Phase 2: Standardization
1. Review all dual wield items in `items.json`
2. Standardize slot definitions for consistency
3. Update documentation

### Phase 3: Integration
1. Replace manual equipment calls with smart equipping
2. Add better error messages for dual wield conflicts
3. Create comprehensive dual wield tests

## Code Changes Required

### 1. Demo Equipment Logic Fix
File: `demo.py` around line 2165

```python
if slot == 'weapon':
    current_weapon = getattr(self.player, 'weapon', None)
    current_offhand = getattr(self.player, 'offhand', None)
    
    # Check if weapon slot is available
    if current_weapon is None:
        # Check for dual wield swap scenario
        if (current_offhand is not None and 
            hasattr(item, 'dual_wield') and item.dual_wield and
            hasattr(current_offhand, 'dual_wield') and current_offhand.dual_wield):
            # Allow swapping offhand to weapon
            slot_available = True
            self.log_message(f"Will swap {current_offhand.name} from offhand to weapon slot", "info")
        else:
            slot_available = True
```

### 2. Equipment Execution Fix
File: `demo.py` around line 2290

```python
# Add dual wield swap logic before equipment
if (slot == 'weapon' and current_weapon is None and current_offhand is not None and
    hasattr(item, 'dual_wield') and item.dual_wield and
    hasattr(current_offhand, 'dual_wield') and current_offhand.dual_wield):
    
    # Temporarily unequip offhand
    offhand_item = current_offhand
    self.player.offhand = None
    
    # Equip new item to weapon
    self.player.equip_weapon(item)
    
    # Re-equip old offhand to weapon (it becomes main weapon)
    # New item should go to offhand instead
    self.player.equip_offhand(item)
    self.player.equip_weapon(offhand_item)
```

## Testing Strategy

### Test Cases
1. **Empty hands → dual wield**: Equip dagger in offhand, then weapon
2. **Reverse order**: Equip dagger in weapon, then offhand  
3. **Incompatible combo**: Try dual wield with non-dual-wield weapons
4. **Full hands**: Try to equip when both slots occupied
5. **Two-handed conflict**: Ensure two-handed weapons prevent dual wield

### Manual Testing Steps
1. Start with empty equipment slots
2. Create and equip `iron_dagger` in offhand slot
3. Create second `iron_dagger` 
4. Attempt to equip in weapon slot
5. Verify both daggers are equipped
6. Test combat with dual wield setup

## Future Improvements

### Enhanced Dual Wield System
1. **Weapon Pairing Rules**: Define which weapons can be dual wielded together
2. **Stat Penalties**: Implement off-hand damage reduction
3. **Special Attacks**: Add dual wield specific combat moves
4. **Animation System**: Visual representation of dual wielding
5. **Balance Tweaks**: Adjust damage/speed for dual wield builds

### UI Improvements
1. **Visual Indicators**: Show dual wield compatibility in inventory
2. **Auto-Swap Options**: Ask user before swapping equipment
3. **Dual Wield Display**: Better visualization of dual wield setup
4. **Conflict Resolution**: Clear messages for equipment conflicts

## Conclusion

The dual wield system has solid foundations but needs better integration between the demo UI and the core actor logic. The recommended approach is to fix the demo's equipment validation to handle reverse dual wield scenarios while maintaining backward compatibility.

Key takeaway: The actor system supports dual wielding, but the demo's manual equipment logic doesn't handle all dual wield scenarios properly.