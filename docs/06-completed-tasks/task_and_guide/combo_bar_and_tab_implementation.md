# Combo Bar and Combo Tab Implementation Guide

This guide outlines the step-by-step process to implement a combo bar in the combat section and a dedicated combo tab in the SimpleGameDemo UI.

---

## Needed Files

- `demo.py`: Main implementation file. Add combo tracking, update spell casting, draw combo bar, and set up combo tab here.
- `game_sys/magic/data/combos.json`: Contains combo definitions and effects. Use for displaying available combos in the combo tab.
- `instructions/combo_bar_and_tab_implementation.md`: This guide and checklist for implementation steps.

---

## 1. Combo Bar in Combat Section

### 1.1. Track Combo State
- Add attributes to `SimpleGameDemo` for combo tracking:
  - `self.combo_sequence = []`  # List of recent spells cast
  - `self.combo_timer = 0`      # Time left in combo window
  - `self.combo_window = 5.0`   # Max seconds to complete a combo
  - `self.last_combo_time = 0`  # Timestamp of last spell cast

### 1.2. Update Combo on Spell Cast
- In spell casting methods (e.g. `cast_fireball`, `cast_ice_shard`):
  - Call a helper: `self._update_combo_sequence("fireball")` or `self._update_combo_sequence("ice_shard")`
- Implement `_update_combo_sequence(spell_id)`:
  - Append spell to `self.combo_sequence`
  - Reset or update `self.combo_timer` and `self.last_combo_time`
  - Trim sequence to max combo length

### 1.3. Draw Combo Bar in Combat UI
- In `draw_game_state`, after stamina bar:
  - Calculate combo progress: `combo_pct = self.combo_timer / self.combo_window`
  - Draw a rectangle below stamina bar, fill based on `combo_pct`
  - Optionally, display current combo sequence as text

### 1.4. Combo Timer Update
- On each game tick or after actions:
  - Decrease `self.combo_timer` based on elapsed time
  - If timer reaches zero, reset `self.combo_sequence`

---

## 2. Combo Tab Implementation

### 2.1. Create Combo Tab
- In `setup_ui`, add a new tab:
  - `self.combo_tab = ttk.Frame(self.tab_control)`
  - `self.tab_control.add(self.combo_tab, text="Combos")`

### 2.2. Combo Tab UI Elements
- In a new method (e.g. `setup_combo_tab`):
  - Display current combo sequence
  - List possible combos (from `game_sys/magic/data/combos.json`)
  - Show combo effects and requirements

### 2.3. Update Combo Tab
- When combo sequence changes or a combo is triggered:
  - Update the combo tab display to show progress and effects

---

## 3. Best Practices
- Use clear visual feedback for combo progress
- Keep UI responsive and update combo bar/tab in real time
- Document combo logic for future improvements

---

**End of Guide**
#!/usr/bin/env python3
"""
Simple Game Demo
===============

A basic demo for the game engine with integrated logging and tabbed interface.
"""

import tkinter as tk
from tkinter import ttk
import time
import random
import math


# Import logging system
from logs.logs import get_logger, setup_logging

# Set up logging
setup_logging()
logger = get_logger("simple_demo")
