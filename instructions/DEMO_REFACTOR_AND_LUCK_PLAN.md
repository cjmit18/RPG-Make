# Demo Refactor and Luck Integration Plan

## 1. Incorporate Luck Into Relevant Modules

**Combat:**
- Add luck as a modifier to critical chance, evasion, and block/parry outcomes.
- Example: `final_crit_chance = base_crit_chance + (luck * luck_crit_factor)`
- Use luck to slightly increase or decrease random rolls for the player (and enemies).

**Loot:**
- Use luck to influence loot rarity and drop rates.
- Example: Higher luck increases the chance of rare/epic drops.

**Other Random Events:**
- Use luck for random events, traps, or skill checks.

**Implementation Steps:**
- Update combat engine to include luck in crit/evasion/block calculations.
- Update loot generation code to factor in luck.
- Add config values for luck scaling factors (e.g., `luck_crit_factor`, `luck_loot_factor`).
- Update UI to display luck's effect where relevant.

## 2. Decouple Demo Into Separate Modules

**Goal:**
- Move UI and logic for each tab (Stats, Combat, Inventory, Leveling, Enchanting, Progression) into separate files/classes.
- Move combat, inventory, and character logic into their own modules/services.
- Use a controller/service layer to coordinate between UI and game logic.

**Suggested Structure:**
- `ui/`
  - `stats_tab.py`
  - `combat_tab.py`
  - `inventory_tab.py`
  - `leveling_tab.py`
  - `enchanting_tab.py`
  - `progression_tab.py`
- `services/`
  - `combat_service.py`
  - `inventory_service.py`
  - `character_service.py`
- `main_demo.py` (entry point, wires up all modules)

**Implementation Steps:**
1. For each tab, move the setup and update logic into a new class in `ui/`.
2. Refactor combat/inventory/character logic into service classes in `services/`.
3. Update the main demo class to instantiate and coordinate these modules.
4. Ensure all UI updates and game logic calls go through the new service/controller layer.
5. Update imports and references throughout the codebase.

**Benefits:**
- Easier maintenance and testing.
- Clear separation of concerns.
- Enables parallel development and future expansion.

---

**This plan provides a roadmap for agents to implement luck integration and demo decoupling efficiently.**
