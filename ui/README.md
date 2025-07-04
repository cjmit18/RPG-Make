# UI and Rendering System

This system provides a modular, extensible architecture for building user interfaces and rendering game visuals.

## Features

### Core UI System (`ui/`)

- **Component-Based Architecture**: Build UIs using reusable, composable widgets
- **Event System**: Handle user interactions with a flexible event system
- **Game-Specific Widgets**: Pre-built widgets for common game UI elements
- **Tkinter Integration**: Built on Tkinter but with an abstraction layer for potential future backends

### Advanced UI Features

- **Animation System**: Animate UI properties with easing functions and sequences
- **Theme System**: Apply consistent styling across the UI with theme support
- **Layout System**: Organize UI elements with flexible layouts (Box, Grid)

### Rendering System (`rendering/`)

- **Render Pipeline**: Efficiently manage rendering operations with layers and priorities
- **Command-Based Rendering**: Submit render commands for batched processing
- **Canvas Integration**: Built on Tkinter Canvas with a clean abstraction layer

## Demos

The system includes several demo applications to showcase its capabilities:

- `simplified_ui_demo.py`: A basic demo of the UI and rendering system
- `modular_ui_demo.py`: Demonstrates the modular UI architecture
- `advanced_ui_demo2.py`: Showcases animations, themes, and layouts

## Usage

### Basic UI Setup

```python
from ui.ui_manager import UIManager
from ui.basic_widgets import Button, Label, Panel

# Create the UI manager
ui_manager = UIManager()
ui_manager.initialize(title="My Game", width=800, height=600)

# Create panels and widgets
main_panel = Panel(title="Main Panel")
main_panel.create_widget(ui_manager.root)

# Add a button
button = Button(main_panel, text="Click Me", command=lambda: print("Clicked!"))
button.create_widget(main_panel._tk_widget)

# Run the UI
ui_manager.run()
```

### Game-Specific Widgets

```python
from ui.game_widgets import CharacterPanel, GameLogPanel, ActionPanel

# Create a character panel
char_panel = CharacterPanel(title="Player")
char_panel.create_widget(ui_manager.root)
char_panel.set_actor(player)  # Set the player character

# Create a game log
log_panel = GameLogPanel()
log_panel.create_widget(ui_manager.root)
log_panel.log("Welcome to the game!", "action")
```

### Using Animations

```python
from ui.animation import EasingType

# Animate a widget property
ui_manager.create_animation(
    widget, "opacity", 1.0, 0.5,
    duration=1.0, easing=EasingType.EASE_IN_OUT
).on_complete(lambda: print("Animation complete!"))

# Chain animations
ui_manager.create_animation(
    widget, "scale", 1.0, 1.5, duration=0.5
).on_complete(lambda: ui_manager.create_animation(
    widget, "scale", 1.5, 1.0, duration=0.5
))
```

### Using Themes

```python
# Set a theme
ui_manager.set_theme("dark")

# Create a custom theme
from ui.theme import Theme, ThemeElement
custom_theme = Theme("custom")
custom_theme.set_color(ThemeElement.BACKGROUND, Color(50, 50, 70))
custom_theme.set_color(ThemeElement.TEXT, Color(220, 220, 240))
theme_manager.register_theme(custom_theme)
ui_manager.set_theme("custom")
```

### Using Layouts

```python
from ui.layout import BoxLayout, GridLayout, LayoutDirection, LayoutConstraints, Alignment

# Create a horizontal box layout
box_layout = BoxLayout(direction=LayoutDirection.HORIZONTAL, spacing=10)
box_layout.create_widget(parent)

# Add widgets with constraints
btn = Button(text="Button 1")
btn.create_widget(box_layout._tk_widget)
box_layout.add(btn, LayoutConstraints(
    preferred_width=100,
    horizontal_alignment=Alignment.CENTER
))
```

### Basic Rendering

```python
from rendering.renderer import TkRenderer
from rendering.render_types import RenderCommand, RenderLayer, Color

# Create a canvas in your UI
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()

# Create the renderer
renderer = TkRenderer(canvas, width=800, height=600)

# Begin a frame
renderer.begin_frame()

# Submit render commands
renderer.submit_command(RenderCommand(
    layer=RenderLayer.BACKGROUND,
    data={
        "type": "rect",
        "x": 0,
        "y": 0,
        "width": 800,
        "height": 600,
        "color": Color(240, 240, 240)
    }
))

# Submit more commands...

# End the frame (triggers actual rendering)
renderer.end_frame()
```

## Architecture

### UI System

- `BaseWidget`: Abstract base class for all UI widgets
- `UIManager`: Manages widgets and UI state
- `UIEvent`: Represents UI events (clicks, hover, etc.)
- `AnimationManager`: Manages animations for UI elements
- `ThemeManager`: Manages themes and styles
- `Layout`: Base class for layout managers

### Rendering System

- `Renderer`: Base renderer class with TkRenderer implementation
- `RenderPipeline`: Processes and orders render commands
- `RenderCommand`: Represents a rendering operation

## Extension

To add new widgets:

1. Extend `BaseWidget` with your custom widget class
2. Implement the `create_widget` method to create the actual Tkinter widget
3. Register any event handlers as needed

To add new rendering capabilities:

1. Add new command types to the renderer's `_process_command` method
2. Implement the drawing logic for the new command type

To add new animation types:

1. Extend the `Animation` class with your custom animation
2. Implement the `update` method to update the animation state
3. Register your animation with the `AnimationManager`
