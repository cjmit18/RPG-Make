# Character Library System

The character library system provides persistent character storage and management for the character creation demo. This system allows users to save, load, manage, and reuse created characters.

## Features

### Character Persistence
- **Save Characters**: Save any created character to the library with a custom name
- **Load Characters**: Load previously saved characters and continue working with them  
- **Character Library**: View and manage all saved characters in an organized interface
- **Delete Characters**: Remove characters from the library when no longer needed

### Storage System
- Characters are stored in `save/character_library.json`
- Each saved character includes:
  - Original character data (stats, level, equipment, etc.)
  - Template information (for proper reconstruction)
  - Save metadata (save name, creation date)
  - Full character state (health, mana, stamina, etc.)

## How to Use

### Saving a Character

1. Create a character using the normal character creation process:
   - Select a template from the dropdown
   - Allocate stat points as desired
   - Preview or finalize the character

2. Click the **"💾 Save Character"** button in the Character Library section

3. Enter a custom save name when prompted (defaults to character name)

4. The character will be saved to the library with all current stats and properties

### Loading a Character

1. Click the **"📂 Load Character"** button

2. Select a character from the list that appears:
   - Each entry shows: Save Name | Character Name | Level | Template
   - Double-click or select and click "Load" to load the character

3. The character will be loaded into the creation interface:
   - All stats and properties restored
   - Template automatically selected  
   - Ready for further modification or use

### Managing the Library

1. Click the **"📋 Manage Library"** button to open the full library manager

2. The library manager provides:
   - **Complete character list** with detailed information
   - **Load functionality** - double-click or use the Load button
   - **Delete functionality** - select character and click Delete  
   - **Refresh** - reload the library if changed externally
   - **Sortable columns** - Save Name, Character Name, Level, Template, Created Date

### Character Creation Integration

The library system is fully integrated with the character creation workflow:

- **Automatic Save Option**: When finalizing a character, it's automatically saved to the library
- **Template Preservation**: Loaded characters maintain their original template selection
- **Stat Allocation**: Loaded characters show their final allocated stats
- **Grade/Rarity**: All character properties including grade and rarity are preserved

## UI Components

### Character Library Section
Located in the character creation interface with three main buttons:

1. **💾 Save Character** - Save current character with custom name
2. **📂 Load Character** - Quick load from character selection dialog  
3. **📋 Manage Library** - Open full library management window

### Library Management Window
Full-featured character management interface:
- **Treeview display** with sortable columns
- **Multi-select operations** (load, delete)
- **Context-sensitive actions**
- **Real-time library updates**

## Technical Details

### File Structure
```json
{
  "SaveName": {
    "name": "Character Display Name",
    "original_name": "Original Character Name", 
    "template_id": "template_identifier",
    "save_name": "Custom Save Name",
    "created_date": "2025-07-20T11:40:02.339347",
    "character_data": "Serialized Character JSON"
  }
}
```

### Integration Points

#### Service Layer
- `CharacterCreationService` handles all library operations
- Integrates with existing character creation workflow
- Maintains separation between business logic and UI

#### UI Layer
- `CharacterCreationUI` provides library interface components
- Callback system for clean service integration
- Modal dialogs for user interactions

## Error Handling

The system provides robust error handling for:

- **File I/O errors** (permission issues, disk space, etc.)
- **Data corruption** (invalid JSON, missing fields)
- **Template compatibility** (missing templates, version changes)  
- **User input validation** (invalid names, duplicate entries)

## Examples

### Basic Save/Load Workflow
1. Select "Hero" template
2. Allocate +2 Strength, +1 Vitality  
3. Click "💾 Save Character"
4. Enter save name: "My Warrior"
5. Character saved successfully

Later:
1. Click "📂 Load Character"
2. Select "My Warrior" from list
3. Character loaded with Hero template and stat allocations intact

### Library Management
1. Click "📋 Manage Library"
2. View all saved characters in organized table
3. Double-click "My Warrior" to load
4. Select "Old Character" and click Delete to remove

## Benefits

- **Character Reuse**: Build a library of favorite character builds
- **Experimentation**: Save different variations of builds for comparison
- **Backup**: Preserve characters before making changes
- **Sharing**: Export/import library files between sessions
- **Organization**: Manage multiple characters with meaningful names

## Future Enhancements

Potential improvements to the system:
- **Export/Import**: Save character library to external files
- **Search/Filter**: Find characters by name, template, or stats
- **Character Variants**: Save multiple versions of the same character
- **Batch Operations**: Bulk delete, rename, or organize characters
- **Character Comparison**: Side-by-side stat comparisons
