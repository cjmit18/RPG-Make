# Stamina Usage for Combat Actions: Implementation Plan

## Overview
This document outlines how to make attacking, dodging, parrying, evading, and blocking consume stamina in the RPG combat system. The goal is to add resource management and tactical depth to combat, requiring players and enemies to manage stamina for each action.

---

## Goals
- Deduct stamina from the actor (player or enemy) after each relevant combat action:
  - Attacking
  - Dodging
  - Parrying
  - Evading
  - Blocking
- Prevent actions if the actor does not have enough stamina.
- Make stamina cost values configurable (via config file).
- Ensure UI and combat feedback reflect stamina usage and failures due to low stamina.

---

## Implementation Steps

1. **Define Stamina Costs in Config**
   - Add stamina cost values for each action in the config (e.g., `constants.combat.stamina_costs.attack`, etc.).
   - Example:
     ```json
     "stamina_costs": {
       "attack": 5,
       "dodge": 8,
       "parry": 6,
       "evade": 7,
       "block": 4
     }
     ```

2. **Update Combat Methods**
   - In the combat engine (e.g., `engine.py` or `combat_service.py`):
     - Before performing each action, check if the actor has enough stamina.
     - If not, prevent the action and provide feedback (e.g., "Too exhausted to dodge!").
     - If yes, deduct the appropriate stamina amount after the action.
   - Example pseudocode:
     ```python
     if actor.current_stamina < stamina_cost:
         return {"success": False, "message": "Not enough stamina!"}
     # ...perform action...
     actor.current_stamina -= stamina_cost
     ```

3. **UI Feedback**
   - Update the UI to show stamina changes after each action.
   - Display messages when actions fail due to low stamina.

4. **Testing**
   - Test all actions with sufficient and insufficient stamina.
   - Ensure stamina cannot go negative.
   - Verify that stamina costs are respected for both player and enemy.

5. **Optional: Stamina Regeneration**
   - Ensure stamina regeneration works as expected between turns or over time.

---

## Files to Edit
- `game_sys/combat/engine.py` or `combat_service.py` (main logic)
- `game_sys/config/default_settings.json` (add stamina costs)
- `demo.py` (UI feedback)
- `tests/` (add/expand stamina-related tests)

---

## Example Pseudocode
```python
# In attack method
stamina_cost = config.get('constants.combat.stamina_costs.attack', 5)
if actor.current_stamina < stamina_cost:
    return {"success": False, "message": "Not enough stamina!"}
# ...perform attack...
actor.current_stamina -= stamina_cost
```

---

## Summary
This plan ensures all major combat actions consume stamina, making resource management a core part of the combat system and increasing tactical depth.
