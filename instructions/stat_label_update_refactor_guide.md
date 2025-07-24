# Stat Label Update Refactor - Step-by-Step Implementation Guide (July 21, 2025)

## Goal
Make the character creation UI's stat label update logic robust to missing/delayed data, always display correct reduced stats and allocatable points, and prevent runtime errors.

## Steps
1. **Check for stat data presence and type**
   - In `_update_stat_labels`, verify that `current_character` exists and has a `stat_data` attribute that is a dict.
2. **Calculate reduced stats**
   - For each stat, sum `base_*` and `allocated_*` if both are present; otherwise, use the raw stat value.
   - Format floats to 1 decimal place, ints as strings.
3. **Display allocatable stat points**
   - Use `stat_data['allocatable_stat_points']` if present, else fallback to `current_character.allocatable_stat_points`.
4. **Update UI only if valid**
   - Only call `update_stat_labels` if the UI service and method exist.
5. **Log errors for all failure cases**
   - Use the integrated logger to record missing data, type errors, or UI update failures.
6. **Test**
   - Run the demo and verify that stats and allocatable points display correctly, even when data is missing or delayed.

## Example
See `.github/memory_bank/2025-07-21_stat_label_update_refactor.md` for the rationale and code pattern.

## Notes
- This pattern should be used for all UI updates that depend on potentially missing or delayed data.
- Consider moving stat label formatting to the service layer for further decoupling in future refactors.
