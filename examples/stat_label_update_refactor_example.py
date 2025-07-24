def _update_stat_labels(self) -> None:
"""
Stat Label Update Refactor - Example Usage

This example demonstrates the robust stat label update pattern for the character creation UI, ensuring correct display and error handling.

Example (from newdemo.py):

    def _update_stat_labels(self) -> None:
        ...
        # See .github/memory_bank/2025-07-21_stat_label_update_refactor.md for full code and rationale

Pattern:
    - Always check for data presence and type before updating UI.
    - Use base+allocated for reduced stats if available.
    - Format all values for user-friendly display.
    - Log errors for all failure cases.

See also: .github/memory_bank/2025-07-21_stat_label_update_refactor.md and instructions/stat_label_update_refactor_guide.md.
"""
