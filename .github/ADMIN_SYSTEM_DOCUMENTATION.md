# Admin/Cheat System Documentation

## Overview

The Character Creation Demo includes a comprehensive admin/cheat system designed for testing, development, and demonstration purposes. This system provides powerful tools to modify character attributes, manage resources, and control system behavior.

## Security Model

### Admin Mode Requirement
- All cheat functions require admin mode to be enabled first
- Admin mode is toggled manually through the UI
- When admin mode is disabled, all cheat functions are automatically deactivated
- Clear visual indicators show when admin mode is active

### Two-Stage Access Control
1. **Admin Mode Toggle** - Basic admin access control
2. **Function-Specific Checks** - Each cheat function validates admin mode before execution

## Admin Features

### 🔧 Admin Mode Toggle
- **Function**: `toggle_admin_mode()`
- **Purpose**: Enable/disable access to cheat functions
- **UI Location**: Admin/Cheat Panel section
- **Visual Feedback**: Clear success/warning messages when toggled

### 📊 Stats Cheats

#### Infinite Stat Points
- **Function**: `toggle_infinite_stat_points()`
- **Purpose**: Remove stat point limitations during character creation
- **Behavior**: 
  - When enabled, stat allocation doesn't consume points
  - Display shows 999 available points as indicator
  - Automatically disabled when admin mode is turned off
- **UI Indicator**: Shows "(CHEAT MODE)" in allocation messages

#### Add Stat Points
- **Function**: `add_stat_points(amount)`
- **Purpose**: Add specific amounts of stat points to available pool
- **Input**: Configurable amount (default: 10)
- **Use Case**: Testing specific stat allocations without infinite mode

### 👤 Character Cheats

#### Grade Modification
- **Function**: `set_character_grade(grade, grade_name)`
- **Purpose**: Instantly change character grade/tier
- **Range**: 0-4 (ONE through FIVE)
- **Effect**: Automatically updates character stats to reflect new grade
- **Validation**: Ensures grade is within valid range

#### Rarity Modification  
- **Function**: `set_character_rarity(rarity)`
- **Purpose**: Instantly change character rarity
- **Options**: COMMON, UNCOMMON, RARE, EPIC, LEGENDARY
- **Effect**: Automatically updates character stats to reflect new rarity
- **Validation**: Ensures rarity is from valid set

### ⚙️ System Controls

#### Template Reloading
- **Function**: `reload_templates()`
- **Purpose**: Hot-reload character templates from disk
- **Use Case**: Testing template changes without restarting demo
- **Effect**: Updates available templates in dropdown

#### Configuration Reloading
- **Function**: Reload configuration files
- **Purpose**: Refresh game configuration without restart
- **Scope**: Reloads ConfigManager and related settings
- **Use Case**: Testing configuration changes during development

#### Demo Restart
- **Function**: Complete application restart
- **Purpose**: Full system reset with new configuration
- **Safety**: Confirmation dialog prevents accidental restarts
- **Technical**: Uses `os.execl()` for clean restart

## Technical Implementation

### Service Layer Integration
```python
# Admin functions are integrated into CharacterCreationService
class CharacterCreationService:
    def __init__(self):
        self.admin_mode = False
        self.infinite_stat_points = False
    
    def toggle_admin_mode(self) -> Dict[str, Any]:
        # Toggle admin mode with validation
    
    def set_character_grade(self, grade: int) -> Dict[str, Any]:
        if not self.admin_mode:
            raise ValueError("Admin mode required")
        # Modify character grade
```

### UI Integration
```python
# Admin callbacks registered with UI service
callbacks = {
    'toggle_admin_mode': self._toggle_admin_mode,
    'show_admin_panel': self._show_admin_panel
}
```

### Stat Point Override
```python
# Modified stat allocation to respect infinite mode
if not self.infinite_stat_points and self.stat_points_available < amount:
    raise ValueError("Not enough stat points")

if not self.infinite_stat_points:
    self.stat_points_available -= amount
```

## Admin Panel UI

### Tabbed Interface
The admin panel uses a notebook widget with three main sections:

1. **📊 Stats Cheats Tab**
   - Infinite stat points toggle
   - Manual stat point addition
   - Input validation and feedback

2. **👤 Character Cheats Tab**  
   - Grade modification (spinbox 0-4)
   - Rarity modification (dropdown selection)
   - Immediate character update

3. **⚙️ System Controls Tab**
   - Template reloading
   - Configuration reloading  
   - Demo restart functionality
   - Real-time admin status display

### Visual Design
- Dark theme with warning colors for admin functions
- Clear visual hierarchy with labeled sections
- Color-coded buttons (red for admin, blue for system, etc.)
- Status displays for current settings

## Usage Examples

### Basic Admin Workflow
1. Click "🔓 Toggle Admin Mode" 
2. Confirm admin mode is enabled
3. Click "🔧 Admin Panel" to open full controls
4. Use any cheat functions as needed
5. Toggle admin mode off when finished

### Testing Character Builds
1. Enable admin mode
2. Enable infinite stat points
3. Allocate stats freely without limitation
4. Test different grade/rarity combinations
5. Save interesting builds to library

### Development Workflow
1. Enable admin mode
2. Modify configuration files
3. Use "Reload Configuration" to test changes
4. Use "Reload Templates" for template changes
5. Use "Restart Demo" for major changes

## Error Handling

### Validation Layers
- Admin mode requirement checked before any cheat function
- Input validation for numeric values (grade, stat points)
- Range validation for grades (0-4) and rarities (valid set)
- Character existence validation before modifications

### User Feedback
- Success messages for completed operations
- Error messages for invalid operations or inputs  
- Warning messages for potentially destructive actions
- Confirmation dialogs for irreversible operations

### Logging Integration
```python
# All admin actions are logged with appropriate levels
self.logger.info("Admin mode ENABLED - Cheat functions activated")
self.logger.warning("Failed to save character to library: {error}")
```

## Development Considerations

### Testing Support
- Infinite stat points for boundary testing
- Grade/rarity manipulation for build testing
- Hot reloading for rapid development iteration
- Demo restart for clean state testing

### Configuration Management
- Admin settings are runtime-only (not persisted)
- Clean separation between normal and admin functionality
- No permanent modification of character templates
- Safe fallbacks when admin mode is disabled

### Future Enhancements
- Character state export/import for testing
- Batch operations for mass testing
- Custom stat value setting (not just allocation)
- Template creation/editing interface
- Configuration file editing interface

## Security Notes

### Intended Use
- Designed for development and testing environments
- Not intended for production character management
- Clear visual indicators prevent accidental use
- No network or file system security implications

### Safe Practices
- Always disable admin mode after testing
- Validate character state after using cheats
- Save legitimate characters before experimenting
- Use character library to preserve valid builds

## Integration Points

### GitHub Workflow
- Admin system documented in `.github/` folder
- Memory bank updated with admin patterns
- Cross-reference with development workflows
- Integration with existing service architecture

### Service Architecture
- Clean separation between admin and normal functions
- Callback-based UI integration
- Error handling consistent with existing patterns
- Logging integration with main system
