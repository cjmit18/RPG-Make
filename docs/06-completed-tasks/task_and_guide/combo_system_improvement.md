# Combo System Improvement, Expansion, and Integration Plan

## 1. Overview
The combo system is a key feature for deepening combat mechanics, rewarding skillful play, and enabling advanced AI behaviors. This plan outlines how to improve, expand, and fully integrate the combo system into the RPG framework, including configuration, UI, AI, and gameplay feedback.

---

## 2. Goals
- **Configurable Combos:** Allow combos to be defined in config files (JSON/YAML), including sequences, timing, effects, and requirements.
- **Player & AI Usage:** Enable both player and AI to execute combos, with AI logic for combo selection and execution.
- **UI Feedback:** Provide clear, dynamic UI feedback for combo progress, readiness, and execution (e.g., combo meters, visual cues).
- **Advanced Mechanics:** Support interrupts, combo mastery, scaling effects, and resource (stamina/mana) integration.
- **Testing & Validation:** Add automated tests for combo logic, config validation, and edge cases.

---

## 3. Implementation Steps

### 3.1. Config-Driven Combos
- **Combo Definitions:**
  - Add a `combos.json` (or similar) in `game_sys/config`.
  - Each combo includes: name, sequence (actions/inputs), timing windows, stamina/mana cost, effects, requirements (stats, equipment, status).
- **Config Validation:**
  - Expand startup validation to check combo config integrity.

### 3.2. Combo Engine Refactor
- **Combo Manager:**
  - Create a `ComboManager` class (e.g., `game_sys/combat/combo_manager.py`).
  - Handles combo state, progress, timing, and effect application for each actor.
- **Integration Points:**
  - Hook into combat action processing to track combo progress and trigger effects.
  - Block or modify actions if combo requirements are not met (e.g., stamina too low).

### 3.3. Player & AI Integration
- **Player:**
  - Allow input sequences (button presses, action choices) to trigger combos.
  - Provide feedback on combo readiness, progress, and success/failure.
- **AI:**
  - Expand AI logic to recognize and attempt combos based on context (enemy state, available resources, tactical value).
  - Add AI weights/priorities for combo usage.

### 3.4. UI/UX Enhancements
- **Combo Meter:**
  - Add a visual combo meter/bar to the combat UI (in `demo.py`).
  - Show current combo progress, timing windows, and readiness.
- **Feedback:**
  - Display messages/logs for combo attempts, successes, failures, and interrupts.
  - Use color/animation to highlight combo events.

### 3.5. Advanced Mechanics
- **Interrupts:**
  - Allow combos to be interrupted by enemy actions, status effects, or resource depletion.
- **Mastery/Scaling:**
  - Add combo mastery (improved effects with repeated use or skill investment).
  - Scale combo effects with stats, equipment, or buffs.
- **Resource Integration:**
  - Deduct stamina/mana for combo actions; block combos if resources are insufficient.

### 3.6. Testing & Validation
- **Automated Tests:**
  - Add/expand tests in `tests/` for combo logic, edge cases, and config validation.
  - Test AI combo usage and UI feedback.
- **Logging:**
  - Log combo events, errors, and config issues at startup and during combat.

---

## 4. Integration Checklist
- [ ] Combo definitions in config
- [ ] ComboManager implementation
- [ ] Player and AI combo usage
- [ ] UI feedback (combo meter, logs)
- [ ] Advanced mechanics (interrupts, mastery)
- [ ] Automated tests
- [ ] Startup/config validation

---

## 5. Future Extensions
- **Combo Customization:** Allow players to create/customize combos.
- **Combo Synergy:** Enable combo chaining and team combos in party-based combat.
- **Replay/Highlight System:** Record and replay impressive combos.

---

## 6. References
- See `game_sys/combat/engine.py`, `demo.py`, and `tests/` for integration points.
- Review existing stamina/mana logic for resource integration.

---

*Prepared July 10, 2025*
