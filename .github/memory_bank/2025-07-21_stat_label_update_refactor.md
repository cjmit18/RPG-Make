# Memory Bank Entry: Stat Label Update Refactor (July 21, 2025)

## Context
- File: `newdemo.py`
- Area: Character creation UI, stat label update logic
- Motivation: Repeated runtime errors (`'stat_data'` missing) and incorrect stat/allocatable point display in the character creation demo UI.

## Problem
- The `_update_stat_labels` method was causing errors when `stat_data` was missing or not a dict.
- Allocatable stat points and reduced stats were not displaying correct values.
- Stat formatting (decimal places) was inconsistent.

## Solution
- Refactored `_update_stat_labels` to:
  - Robustly check for the presence and type of `stat_data` before updating labels.
  - Sum `base_*` and `allocated_*` for each stat if available, otherwise fallback to the raw stat value.
  - Format all stat values to 1 decimal place if float, else as int.
  - Always display the correct value for allocatable stat points, using both `stat_data` and character attribute fallback.
  - Only update UI if the UI service and update method are present.
- Added error logging for all failure cases.
- Ensured no UI update is attempted if data is missing or malformed.

## Impact
- No more runtime errors when stat data is missing or delayed.
- Stat and allocatable point displays are now always accurate and user-friendly.
- UI is robust to partial or missing data, improving user experience and testability.

## Next Steps
- Consider centralizing stat label formatting in the service layer for even greater decoupling.
- Add integration tests for stat allocation and display logic.
- Document this pattern in the implementation guides for future UI/service refactors.
