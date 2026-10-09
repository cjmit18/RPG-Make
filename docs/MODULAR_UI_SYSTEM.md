# 🎨 Modular UI System Documentation

**Complete Guide to Easy Expandable Application Creation**

---

## 📋 Table of Contents

1. [Overview & Philosophy](#overview--philosophy)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Builder Pattern APIs](#builder-pattern-apis)
5. [Custom Game Widgets](#custom-game-widgets)
6. [Template System](#template-system)
7. [JSON Configuration](#json-configuration)
8. [Event Integration](#event-integration)
9. [Advanced Features](#advanced-features)
10. [Examples & Recipes](#examples--recipes)

---

## 🎯 Overview & Philosophy

The Modular UI System is designed around the principle that **creating complex applications should be simple**. Instead of writing hundreds of lines of tkinter code, you can create sophisticated UIs with just a few declarative statements.

### Core Philosophy

- **Declarative over Imperative**: Describe what you want, not how to build it
- **Composable Components**: Build complex UIs from simple, reusable parts
- **Configuration-Driven**: Everything can be configured through JSON or code
- **Game-Ready**: Built-in widgets for common game UI patterns
- **Extensible**: Easy to add custom widgets and behaviors

### Key Benefits

✅ **Minimal Code**: Create complex UIs with just a few lines  
✅ **Rapid Prototyping**: Build and iterate on UIs quickly  
✅ **Consistent Styling**: Automatic theming and layout management  
✅ **Event Integration**: Seamless integration with the RPG Engine event system  
✅ **Modular Design**: Easy to extend and customize  

---

## 🚀 Quick Start

### Installation & Setup

```python
from rpg_engine.ui import (
    ModularUIManager, UIBuilder, FormBuilder, 
    register_game_widgets
)
from rpg_engine.core.service_container import ServiceContainer
from rpg_engine.core.event_bus import EventBus

# Initialize the system
service_container = ServiceContainer()
service_container.register_singleton(EventBus, EventBus)
service_container.register_singleton(ModularUIManager, ModularUIManager)

# Get UI manager and register game widgets
ui_manager = await service_container.get_service(ModularUIManager)
register_game_widgets(ui_manager)
```

### Your First Application (3 Lines!)

```python
# Create a simple window
app_ui = UIBuilder("My App") \\
    .with_size(400, 200) \\
    .add_label("Hello, World!") \\
    .add_button("Click Me", command="say_hello") \\
    .with_command("say_hello", lambda: print("Hello!")) \\
    .build()

# Run it
app = ui_manager.create_application(app_ui)
app.run()
```

### Complete Form (5 Lines!)

```python
# Create a registration form
form_ui = FormBuilder("User Registration") \\
    .add_text_field("name", "Full Name:") \\
    .add_text_field("email", "Email:") \\
    .add_dropdown("role", "Role:", ["Admin", "User", "Guest"]) \\
    .add_submit_button("Register", "handle_submit") \\
    .build()

form_ui.commands["handle_submit"] = lambda: print("Form submitted!")
app = ui_manager.create_application(form_ui)
app.run()
```

---

## 🏗️ Core Components

### ModularUIManager

The main coordinator for the UI system. Handles widget factories, variables, and application lifecycle.

```python
# Core manager functionality
ui_manager.register_custom_factory('my_widget', MyWidgetFactory())
ui_manager.set_command('my_action', my_function)
ui_manager.get_variable('user_name')
ui_manager.create_application(ui_definition)
```

### UIDefinition

Complete specification of a UI application.

```python
@dataclass
class UIDefinition:
    title: str = "Application"
    geometry: str = "800x600"
    widgets: List[WidgetConfig] = field(default_factory=list)
    commands: Dict[str, Callable] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    on_init: Optional[Callable] = None
    on_close: Optional[Callable] = None
    # ... more fields
```

### WidgetConfig

Configuration for individual widgets.

```python
@dataclass
class WidgetConfig:
    widget_type: Union[WidgetType, str]
    text: str = ""
    value: Any = None
    command: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)
    layout: Dict[str, Any] = field(default_factory=dict)
    children: List['WidgetConfig'] = field(default_factory=list)
```

---

## 🔨 Builder Pattern APIs

### UIBuilder - General Purpose Builder

The most flexible builder for creating any type of UI.

```python
ui = UIBuilder("My Application") \\
    .with_size(800, 600) \\
    .with_theme("clam") \\
    .with_layout(LayoutType.GRID) \\
    .add_label("Welcome!") \\
    .add_button("Start", command="start_action") \\
    .add_entry(variable="user_input") \\
    .begin_frame("Controls") \\
        .add_checkbutton("Enable feature", variable="feature_enabled") \\
        .add_scale(from_=0, to=100, variable="volume") \\
    .end_container() \\
    .with_command("start_action", handle_start) \\
    .build()
```

#### Available Widgets

| Method | Widget Type | Description |
|--------|-------------|-------------|
| `add_label(text)` | Label | Static text display |
| `add_button(text, command)` | Button | Clickable button |
| `add_entry(variable)` | Entry | Single-line text input |
| `add_text(value)` | Text | Multi-line text area |
| `add_listbox(items)` | Listbox | Scrollable item list |
| `add_combobox(values)` | Combobox | Dropdown selection |
| `add_checkbutton(text)` | Checkbutton | Boolean checkbox |
| `add_radiobutton(text)` | Radiobutton | Single selection |
| `add_scale(from_, to)` | Scale | Numeric slider |
| `add_progressbar()` | Progressbar | Progress indicator |
| `add_separator()` | Separator | Visual divider |

#### Container Management

```python
# Create nested layouts
ui.begin_frame("Section Title") \\
    .add_label("Content inside frame") \\
    .add_button("Action") \\
.end_container() \\
.begin_notebook() \\
    .begin_frame("Tab 1") \\
        .add_label("Tab 1 content") \\
    .end_container() \\
    .begin_frame("Tab 2") \\
        .add_label("Tab 2 content") \\
    .end_container() \\
.end_container()
```

#### Layout Control

```python
# Grid layout
ui.add_label("Name:") \\
.with_grid_layout(row=0, column=0, sticky='w') \\
.add_entry(variable="name") \\
.with_grid_layout(row=0, column=1, sticky='ew')

# Pack layout  
ui.add_button("OK") \\
.with_pack_layout(side='left', padx=5) \\
.add_button("Cancel") \\
.with_pack_layout(side='right', padx=5)
```

### FormBuilder - Specialized Form Creator

Optimized for creating data entry forms with automatic layout.

```python
form = FormBuilder("Data Entry Form") \\
    .add_text_field("first_name", "First Name:", required=True) \\
    .add_text_field("last_name", "Last Name:", required=True) \\
    .add_password_field("password", "Password:") \\
    .add_dropdown("department", "Department:", 
                  ["Engineering", "Sales", "Marketing"]) \\
    .add_checkbox_field("newsletter", "Subscribe to newsletter") \\
    .add_text_area("comments", "Comments:", rows=4) \\
    .add_button_row([
        {'text': 'Save', 'command': 'save_form'},
        {'text': 'Cancel', 'command': 'cancel_form'}
    ]) \\
    .build()
```

### DialogBuilder - Dialog Windows

Create modal dialogs and popup windows.

```python
dialog = DialogBuilder("Confirmation") \\
    .with_message("Are you sure you want to delete this item?") \\
    .with_buttons([
        {'text': 'Yes', 'command': 'confirm_delete'},
        {'text': 'No', 'command': 'cancel_delete'}
    ]) \\
    .build()

# Input dialog
input_dialog = DialogBuilder("Enter Name") \\
    .with_message("Please enter your name:") \\
    .with_input("Name:", "user_name") \\
    .with_buttons([
        {'text': 'OK', 'command': 'handle_ok'},
        {'text': 'Cancel', 'command': 'handle_cancel'}
    ]) \\
    .build()
```

### MenuBuilder - Menu Systems

Create application menus with keyboard shortcuts.

```python
menu = MenuBuilder() \\
    .add_menu("File") \\
        .add_item("New", "file_new", "Ctrl+N") \\
        .add_item("Open", "file_open", "Ctrl+O") \\
        .add_separator() \\
        .add_item("Exit", "file_exit", "Ctrl+Q") \\
    .end_menu() \\
    .add_menu("Edit") \\
        .add_item("Cut", "edit_cut", "Ctrl+X") \\
        .add_item("Copy", "edit_copy", "Ctrl+C") \\
        .add_item("Paste", "edit_paste", "Ctrl+V") \\
    .end_menu() \\
    .build()
```

---

## 🎮 Custom Game Widgets

The system includes specialized widgets for game interfaces.

### Character Stats Display

```python
# Character stats with automatic layout
stats_widget = WidgetConfig(
    widget_type='character_stats',
    text='Character Stats',
    value={
        'strength': 15,
        'dexterity': 12,
        'intelligence': 18,
        'health': 140,
        'mana': 180
    }
)

# Update stats dynamically
update_character_stats(widget, {'strength': 16, 'health': 150})
```

### Health/Mana Bars

```python
# Health bar with custom styling
health_bar = WidgetConfig(
    widget_type='health_bar',
    text='Health',
    value=85,
    options={'max_value': 100, 'color': 'red'}
)

# Update bar value
update_health_bar(widget, current=95, maximum=120)
```

### Inventory Grid

```python
# Interactive inventory grid
inventory = WidgetConfig(
    widget_type='inventory_grid',
    text='Inventory',
    options={'rows': 5, 'cols': 5, 'slot_size': 40}
)

# Add items to slots
add_inventory_item(widget, row=0, col=1, item_data={
    'name': 'Iron Sword',
    'type': 'weapon',
    'rarity': 'common'
})
```

### Combat Log

```python
# Scrolling combat messages
combat_log = WidgetConfig(
    widget_type='combat_log',
    text='Combat Log'
)

# Add messages with styling
add_combat_message(widget, "You hit the goblin for 15 damage!", "damage")
add_combat_message(widget, "You gained 25 experience points.", "system")
```

### Complete Game HUD

```python
# Full game interface in one widget
game_hud = WidgetConfig(
    widget_type='game_hud'
)

# The HUD includes:
# - Health, mana, and experience bars
# - Minimap
# - Chat system
# - All automatically laid out and functional
```

### Available Game Widgets

| Widget Type | Description | Use Case |
|-------------|-------------|----------|
| `character_stats` | Stat display panel | Character sheet, tooltips |
| `health_bar` | Progress bar with text | Health, mana, experience |
| `inventory_grid` | Clickable item grid | Inventory, bank, shop |
| `skill_tree` | Scrollable skill list | Character progression |
| `combat_log` | Styled message log | Combat feedback |
| `minimap` | Game world map | Navigation aid |
| `chat_system` | Chat input/display | Multiplayer communication |
| `achievement_panel` | Achievement list | Player progression |
| `game_hud` | Complete game UI | Main game interface |

---

## 📋 Template System

Pre-built templates for common application patterns.

### CRUD Interface Template

```python
# Complete data management interface
crud_ui = UITemplate.create_crud_interface("Product")

# Automatically includes:
# - Item list on the left
# - Detail form on the right  
# - Save/Delete/New buttons
# - Proper layout and styling

crud_ui.commands = {
    'save_item': handle_save,
    'delete_item': handle_delete,
    'new_item': handle_new
}
```

### Settings Dialog Template

```python
# Standard settings dialog
settings_ui = UITemplate.create_settings_dialog()

# Includes:
# - Tabbed interface (General, Advanced)
# - Common settings controls
# - OK/Cancel/Apply buttons
```

### Data Viewer Template

```python
# Spreadsheet-style data viewer
viewer_ui = UITemplate.create_data_viewer(
    title="Sales Data",
    columns=["Date", "Product", "Amount", "Customer"]
)

# Includes:
# - Toolbar with Refresh/Export/Filter
# - Sortable columns
# - Built-in scrolling
```

### Custom Templates

Create your own templates for reuse:

```python
class MyTemplates:
    @staticmethod
    def create_login_screen():
        return UIBuilder("Login") \\
            .with_size(350, 200) \\
            .add_label("Please log in", font=('Arial', 14, 'bold')) \\
            .with_pack_layout(pady=20) \\
            .add_text_field("username", "Username:") \\
            .add_password_field("password", "Password:") \\
            .add_button_row([
                {'text': 'Login', 'command': 'handle_login'},
                {'text': 'Cancel', 'command': 'handle_cancel'}
            ]) \\
            .build()
    
    @staticmethod
    def create_dashboard():
        return UIBuilder("Dashboard") \\
            .with_size(1200, 800) \\
            .begin_paned_window(orient='horizontal') \\
                .begin_frame("Navigation") \\
                    # Navigation menu
                .end_container() \\
                .begin_frame("Content") \\
                    # Main content area
                .end_container() \\
            .end_container() \\
            .build()
```

---

## 📄 JSON Configuration

Create UIs entirely from JSON configuration files.

### Basic JSON Structure

```json
{
    "title": "My Application",
    "geometry": "800x600",
    "style_theme": "clam",
    "layout_type": "grid",
    "variables": {
        "user_name": "Default User",
        "auto_save": true
    },
    "widgets": [
        {
            "type": "label",
            "text": "Welcome to My App",
            "options": {"font": ["Arial", 16, "bold"]},
            "layout": {"row": 0, "column": 0, "pady": 20}
        },
        {
            "type": "entry",
            "variable": "user_name",
            "layout": {"row": 1, "column": 0, "sticky": "ew"}
        },
        {
            "type": "button",
            "text": "Submit",
            "command": "handle_submit",
            "layout": {"row": 2, "column": 0, "pady": 10}
        }
    ],
    "menus": [
        {
            "label": "File",
            "items": [
                {"label": "New", "command": "file_new", "accelerator": "Ctrl+N"},
                {"label": "Open", "command": "file_open", "accelerator": "Ctrl+O"},
                {"separator": true},
                {"label": "Exit", "command": "file_exit"}
            ]
        }
    ]
}
```

### Loading JSON Configuration

```python
# From file
ui_def = ui_manager.load_ui_from_json("my_app.json")

# From dictionary
config_dict = {...}  # JSON data as dict
ui_def = ui_manager.load_ui_from_dict(config_dict)

# Add runtime commands
ui_def.commands["handle_submit"] = my_submit_handler
ui_def.commands["file_new"] = my_new_handler

# Run the application
app = ui_manager.create_application(ui_def)
app.run()
```

### Advanced JSON Features

```json
{
    "widgets": [
        {
            "type": "labelframe",
            "text": "User Information",
            "layout": {"row": 0, "column": 0, "sticky": "ew"},
            "children": [
                {
                    "type": "label",
                    "text": "Name:",
                    "layout": {"row": 0, "column": 0, "sticky": "w"}
                },
                {
                    "type": "entry",
                    "variable": "name",
                    "validation": {"required": true, "min_length": 2},
                    "layout": {"row": 0, "column": 1, "sticky": "ew"}
                }
            ]
        }
    ],
    "styles": {
        "Title.TLabel": {
            "font": ["Arial", 18, "bold"],
            "foreground": "blue"
        }
    }
}
```

---

## 🔄 Event Integration

Seamless integration with the RPG Engine event system.

### Event-Driven Updates

```python
# UI responds to game events automatically
@ui_manager.event_bus.subscribe(CharacterLevelUpEvent)
def on_character_levelup(event):
    # Update character display
    char_widget = ui_manager.get_widget('character_stats')
    update_character_stats(char_widget, event.character.stats)
    
    # Update health bar
    health_widget = ui_manager.get_widget('health_bar')
    update_health_bar(health_widget, event.character.health, event.character.max_health)

# UI can publish events
def on_button_click():
    ui_manager.event_bus.publish(UserActionEvent(action="button_clicked"))
```

### Real-Time Updates

```python
# Connect UI to live game data
class GameUI:
    def __init__(self, ui_manager, game_engine):
        self.ui_manager = ui_manager
        self.game_engine = game_engine
        
        # Subscribe to relevant events
        game_engine.event_bus.subscribe(HealthChangedEvent, self.update_health)
        game_engine.event_bus.subscribe(InventoryChangedEvent, self.update_inventory)
    
    def update_health(self, event):
        health_bar = self.ui_manager.get_widget('health_bar')
        update_health_bar(health_bar, event.current_health, event.max_health)
    
    def update_inventory(self, event):
        inventory_grid = self.ui_manager.get_widget('inventory')
        # Update inventory display
```

---

## 🔧 Advanced Features

### Custom Widget Factories

Create your own widget types:

```python
class CustomGaugeFactory(WidgetFactory):
    def create_widget(self, parent, config, ui_manager):
        frame = ttk.Frame(parent)
        
        # Create custom gauge widget
        canvas = tk.Canvas(frame, width=200, height=20)
        canvas.pack()
        
        # Custom drawing logic
        self.draw_gauge(canvas, config.value, config.options.get('max_value', 100))
        
        return frame
    
    def draw_gauge(self, canvas, value, max_value):
        # Custom gauge drawing implementation
        pass

# Register the factory
ui_manager.register_custom_factory('custom_gauge', CustomGaugeFactory())

# Use in UI definition
gauge_widget = WidgetConfig(
    widget_type='custom_gauge',
    value=75,
    options={'max_value': 100, 'color': 'green'}
)
```

### Dynamic UI Modification

```python
# Add widgets at runtime
new_button = WidgetConfig(
    widget_type=WidgetType.BUTTON,
    text="Dynamic Button",
    command="dynamic_action"
)

app.add_widget(new_button, parent_id="button_container")

# Remove widgets
app.remove_widget("old_button")

# Update widget properties
app.update_widget("status_label", text="Updated Status", style={'foreground': 'red'})
```

### Validation System

```python
# Built-in validation
entry_config = WidgetConfig(
    widget_type=WidgetType.ENTRY,
    variable="email",
    validation={
        'required': True,
        'pattern': r'^[\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}$',
        'message': 'Please enter a valid email address'
    }
)

# Custom validation
def validate_username(value):
    if len(value) < 3:
        return False, "Username must be at least 3 characters"
    if not value.isalnum():
        return False, "Username must contain only letters and numbers"
    return True, ""

ui_def.validators['username'] = validate_username
```

### Theming and Styling

```python
# Custom themes
ui_def.styles = {
    'Title.TLabel': {
        'font': ('Arial', 18, 'bold'),
        'foreground': '#333333',
        'background': '#f0f0f0'
    },
    'Action.TButton': {
        'font': ('Arial', 10, 'bold'),
        'foreground': 'white',
        'background': '#007acc'
    }
}

# Apply theme to specific widgets
widget_config.style = 'Title.TLabel'
```

---

## 📚 Examples & Recipes

### Recipe 1: Data Entry Form with Validation

```python
def create_user_form():
    form = FormBuilder("New User Registration") \\
        .add_text_field("username", "Username:", required=True) \\
        .add_password_field("password", "Password:") \\
        .add_password_field("confirm_password", "Confirm Password:") \\
        .add_text_field("email", "Email Address:") \\
        .add_dropdown("role", "User Role:", ["User", "Admin", "Moderator"]) \\
        .add_checkbox_field("terms", "I agree to the terms of service") \\
        .add_button_row([
            {'text': 'Create User', 'command': 'create_user'},
            {'text': 'Cancel', 'command': 'cancel'}
        ]) \\
        .build()
    
    def validate_and_create():
        # Validation logic
        username = ui_manager.get_variable("username").get()
        password = ui_manager.get_variable("password").get()
        confirm = ui_manager.get_variable("confirm_password").get()
        
        if len(username) < 3:
            messagebox.showerror("Error", "Username too short")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match")
            return
        
        # Create user
        messagebox.showinfo("Success", f"User {username} created successfully!")
    
    form.commands["create_user"] = validate_and_create
    form.commands["cancel"] = lambda: app.destroy()
    
    return form
```

### Recipe 2: Real-Time Dashboard

```python
def create_dashboard():
    dashboard = UIBuilder("System Dashboard") \\
        .with_size(1200, 800) \\
        .add_label("System Status Dashboard", font=('Arial', 16, 'bold')) \\
        .with_pack_layout(pady=10) \\
        .begin_frame("Metrics") \\
            .add_label("CPU Usage:") \\
            .with_pack_layout(anchor='w') \\
            .add_progressbar(length=300, mode='determinate') \\
            .with_pack_layout(fill='x', pady=5) \\
            .add_label("Memory Usage:") \\
            .with_pack_layout(anchor='w') \\
            .add_progressbar(length=300, mode='determinate') \\
            .with_pack_layout(fill='x', pady=5) \\
        .end_container() \\
        .with_pack_layout(fill='x', padx=20, pady=10) \\
        .begin_paned_window(orient='horizontal') \\
            .begin_frame("Active Processes") \\
                .add_listbox(variable="process_list") \\
                .with_pack_layout(fill='both', expand=True) \\
            .end_container() \\
            .begin_frame("Log Messages") \\
                .add_text(height=20) \\
                .with_pack_layout(fill='both', expand=True) \\
            .end_container() \\
        .end_container() \\
        .with_pack_layout(fill='both', expand=True, padx=20, pady=10) \\
        .build()
    
    # Real-time updates
    def update_metrics():
        # Update CPU/memory bars
        # Add log messages
        # Refresh process list
        root.after(1000, update_metrics)  # Update every second
    
    dashboard.on_init = lambda app: update_metrics()
    return dashboard
```

### Recipe 3: Game Character Sheet

```python
def create_character_sheet():
    sheet = UIBuilder("Character Sheet") \\
        .with_size(800, 600) \\
        .begin_notebook() \\
            .begin_frame("Stats") \\
                .add_label("Primary Stats", font=('Arial', 12, 'bold')) \\
                .with_pack_layout(pady=10) \\
                .begin_frame() \\
                    .add_label("Strength: 15 (+2)") \\
                    .with_pack_layout(anchor='w') \\
                    .add_label("Dexterity: 12 (+1)") \\
                    .with_pack_layout(anchor='w') \\
                    .add_label("Intelligence: 18 (+4)") \\
                    .with_pack_layout(anchor='w') \\
                .end_container() \\
                .with_pack_layout(side='left', padx=20) \\
                .begin_frame() \\
                    .add_label("Health: 140/140") \\
                    .with_pack_layout(anchor='w') \\
                    .add_label("Mana: 180/180") \\
                    .with_pack_layout(anchor='w') \\
                    .add_label("Stamina: 100/100") \\
                    .with_pack_layout(anchor='w') \\
                .end_container() \\
                .with_pack_layout(side='left', padx=20) \\
            .end_container() \\
            .begin_frame("Equipment") \\
                .add_label("Equipped Items", font=('Arial', 12, 'bold')) \\
                .with_pack_layout(pady=10) \\
                .add_text(value="Weapon: Iron Sword (+15 ATK)\\nArmor: Leather Armor (+5 DEF)\\nAccessory: Ring of Protection (+10 HP)") \\
                .with_pack_layout(fill='both', expand=True, padx=20) \\
            .end_container() \\
            .begin_frame("Skills") \\
                .add_label("Learned Skills", font=('Arial', 12, 'bold')) \\
                .with_pack_layout(pady=10) \\
                .add_listbox(items=["Fireball (Level 3)", "Heal (Level 2)", "Shield (Level 1)"]) \\
                .with_pack_layout(fill='both', expand=True, padx=20) \\
            .end_container() \\
        .end_container() \\
        .with_pack_layout(fill='both', expand=True, padx=10, pady=10) \\
        .build()
    
    return sheet
```

### Recipe 4: Settings Management

```python
def create_settings_manager():
    settings = UIBuilder("Application Settings") \\
        .with_size(600, 500) \\
        .begin_notebook() \\
            .begin_frame("General") \\
                .add_checkbox_field("auto_save", "Auto-save changes") \\
                .add_checkbox_field("show_tooltips", "Show tooltips") \\
                .add_checkbox_field("sound_effects", "Enable sound effects") \\
                .add_separator() \\
                .with_pack_layout(fill='x', pady=10) \\
                .add_label("Language:") \\
                .with_pack_layout(anchor='w') \\
                .add_combobox(values=["English", "Spanish", "French", "German"], variable="language") \\
                .with_pack_layout(fill='x', pady=5) \\
                .add_label("Theme:") \\
                .with_pack_layout(anchor='w') \\
                .add_combobox(values=["Default", "Dark", "Light", "Blue"], variable="theme") \\
                .with_pack_layout(fill='x', pady=5) \\
            .end_container() \\
            .begin_frame("Advanced") \\
                .add_label("Log Level:") \\
                .with_pack_layout(anchor='w') \\
                .add_combobox(values=["DEBUG", "INFO", "WARNING", "ERROR"], variable="log_level") \\
                .with_pack_layout(fill='x', pady=5) \\
                .add_checkbox_field("debug_mode", "Enable debug mode") \\
                .add_checkbox_field("performance_monitoring", "Performance monitoring") \\
                .add_separator() \\
                .with_pack_layout(fill='x', pady=10) \\
                .add_label("Max Memory Usage (MB):") \\
                .with_pack_layout(anchor='w') \\
                .add_scale(from_=128, to=2048, variable="max_memory") \\
                .with_pack_layout(fill='x', pady=5) \\
            .end_container() \\
        .end_container() \\
        .with_pack_layout(fill='both', expand=True, padx=20, pady=20) \\
        .add_button_row([
            {'text': 'Save', 'command': 'save_settings'},
            {'text': 'Cancel', 'command': 'cancel_settings'},
            {'text': 'Apply', 'command': 'apply_settings'},
            {'text': 'Reset', 'command': 'reset_settings'}
        ]) \\
        .build()
    
    def save_settings():
        # Save all settings to file
        messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def apply_settings():
        # Apply settings without closing dialog
        messagebox.showinfo("Settings", "Settings applied!")
    
    settings.commands.update({
        'save_settings': save_settings,
        'cancel_settings': lambda: app.destroy(),
        'apply_settings': apply_settings,
        'reset_settings': lambda: messagebox.askquestion("Reset", "Reset all settings to defaults?")
    })
    
    return settings
```

---

## 🎯 Best Practices

### 1. Keep It Simple
- Start with basic builders before creating custom components
- Use templates for common patterns
- Leverage JSON configuration for data-driven UIs

### 2. Consistent Naming
- Use descriptive names for variables and commands
- Follow consistent naming conventions across your application
- Group related functionality together

### 3. Event-Driven Architecture
- Use the event system for loose coupling between components
- Subscribe to relevant game events for real-time updates
- Publish custom events for application-specific logic

### 4. Performance Considerations
- Use appropriate layout managers for your use case
- Implement lazy loading for complex UIs
- Cache frequently accessed widgets

### 5. Error Handling
- Implement proper validation for user inputs
- Provide clear error messages
- Handle edge cases gracefully

---

## 🔧 Troubleshooting

### Common Issues

**Q: My UI isn't showing up**
```python
# Make sure you're calling run() on the application
app = ui_manager.create_application(ui_def)
app.run()  # Don't forget this!
```

**Q: Commands aren't working**
```python
# Ensure commands are properly registered
ui_def.commands["my_command"] = my_function

# Or use the builder
ui.with_command("my_command", my_function)
```

**Q: Layout looks wrong**
```python
# Check your layout configuration
.with_grid_layout(row=0, column=0, sticky='ew', padx=5, pady=5)

# Make sure container hierarchy is correct
.begin_frame()
    # widgets go here
.end_container()
```

**Q: Custom widgets not working**
```python
# Register your custom factory
ui_manager.register_custom_factory('my_widget', MyWidgetFactory())

# Make sure factory implements WidgetFactory protocol
class MyWidgetFactory(WidgetFactory):
    def create_widget(self, parent, config, ui_manager):
        # Implementation here
        pass
```

---

## 📖 Reference

### Quick Reference

```python
# Essential imports
from rpg_engine.ui import (
    ModularUIManager, UIBuilder, FormBuilder, 
    register_game_widgets
)

# Basic pattern
ui = UIBuilder("App") \\
    .add_widget_type(options) \\
    .with_command("name", function) \\
    .build()

app = ui_manager.create_application(ui)
app.run()
```

### Widget Types Reference

| Type | Builder Method | Options |
|------|----------------|---------|
| Label | `add_label(text)` | `font`, `foreground`, `background` |  
| Button | `add_button(text, command)` | `font`, `state`, `relief` |
| Entry | `add_entry(variable)` | `show`, `state`, `validate` |
| Text | `add_text(value)` | `height`, `width`, `wrap` |
| Listbox | `add_listbox(items)` | `height`, `selectmode` |
| Combobox | `add_combobox(values)` | `state`, `height` |

This completes the comprehensive documentation for the Modular UI System. The system provides powerful yet simple tools for creating complex applications with minimal code while maintaining flexibility and extensibility.
