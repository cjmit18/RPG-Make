# Save/Load System Review & TODO

## Current State

### 1. Actor Save/Load
- `Actor.serialize()` saves all core stats, status, and inventory (via `inventory.list_items()`).
- `Actor.deserialize()` restores all core stats, but **does NOT restore inventory items** (inventory field is ignored on load).
- Inventory is saved as a list of item objects or IDs, but not reloaded into the actor's inventory on load.

### 2. Party/World Save/Load
- `save_actors_async`/`load_actors_async` save/load a list of actors to/from a file.
- Uses async I/O and emits pre/post modding hooks.
- Error handling is present.

### 3. Engine Integration
- `Engine.save_game_async`/`load_game_async` save/load all managed actors.
- On load, unregisters all old actors and registers loaded ones.

### 4. UI Integration (Demo)
- UI buttons call async save/load for player and enemy only.
- User feedback and error handling are present.

## Issues/Limitations
- **Inventory is not restored on load:**
  - Items are saved, but not reloaded into the actor's inventory.
  - No deserialization logic for inventory in `Actor.deserialize()`.
- **Item objects may not be fully serializable:**
  - If items are complex objects, saving them as-is may not work across sessions.
  - Best practice: save only item IDs, and reconstruct items using `load_item(item_id)` on load.
- **Other systems (skills, passives, equipment, world state) may not be fully saved/restored.**
- **Demo UI only saves player/enemy, not full party/world.**

## Recommended Next Steps (TODO)

## Current Capabilities

- Actor save/load supports all core stats, level, XP, health/mana/stamina, grade, rarity, gold, statuses, and skills.
- Inventory is saved as a list (but not restored on load).
- Party/world save/load is supported for lists of actors (async, with modding hooks).
- Engine can save/load all managed actors.
- UI can save/load player and enemy (with user feedback and error handling).

## Not Yet Supported

- Inventory restoration on load (items are not reloaded into inventory).
- Equipment, skills, passives, and world state are not fully restored.
- Demo UI only saves/loads player and enemy, not the full party/world.

---

**Summary:**
- Saving is robust for stats and basic actor data, but inventory and equipment restoration is not yet implemented.
- Next steps: implement inventory deserialization, standardize item ID usage, and expand save/load coverage for all gameplay systems.
