"""
Modular UI System - Easy expandable application creation
Provides simple syntax for building complex UI applications with minimal code

Key Features:
- Declarative UI definition using simple dictionaries
- Automatic event handling and data binding
- Pluggable widget system with custom components
- Automatic layout management
- Configuration-driven styling
- Service integration
"""
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, colorchooser
from typing import Dict, Any, Optional, Callable, List, Union, Protocol
import logging
from abc import ABC, abstractmethod
import json
from dataclasses import dataclass, field
from enum import Enum
import threading

from ..core.service_container import ServiceContainer, AsyncInitializable, AsyncShutdownable
from ..core.event_bus import EventBus, GameEvent, UIUpdateEvent
from .ui_system import UIComponent

logger = logging.getLogger(__name__)

# ============================================================================
# Core Types and Protocols
# ============================================================================

class LayoutType(Enum):
    """Layout management types"""
    GRID = "grid"
    PACK = "pack" 
    PLACE = "place"
    NOTEBOOK = "notebook"
    PANED = "paned"

class WidgetType(Enum):
    """Built-in widget types"""
    LABEL = "label"
    BUTTON = "button"
    ENTRY = "entry"
    TEXT = "text"
    LISTBOX = "listbox"
    TREEVIEW = "treeview"
    COMBOBOX = "combobox"
    SPINBOX = "spinbox"
    SCALE = "scale"
    CHECKBUTTON = "checkbutton"
    RADIOBUTTON = "radiobutton"
    FRAME = "frame"
    LABELFRAME = "labelframe"
    NOTEBOOK = "notebook"
    PANEDWINDOW = "panedwindow"
    CANVAS = "canvas"
    PROGRESSBAR = "progressbar"
    SEPARATOR = "separator"
    SCROLLBAR = "scrollbar"
    MENU = "menu"
    TOOLBAR = "toolbar"
    STATUSBAR = "statusbar"

@dataclass
class WidgetConfig:
    """Configuration for a widget"""
    widget_type: Union[WidgetType, str]
    text: str = ""
    value: Any = None
    command: Optional[str] = None
    variable: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)
    layout: Dict[str, Any] = field(default_factory=dict)
    bindings: Dict[str, str] = field(default_factory=dict)
    children: List['WidgetConfig'] = field(default_factory=list)
    validation: Optional[Dict[str, Any]] = None
    tooltip: Optional[str] = None
    enabled: bool = True
    visible: bool = True

@dataclass 
class UIDefinition:
    """Complete UI definition"""
    title: str = "Modular UI Application" 
    geometry: str = "800x600"
    icon: Optional[str] = None
    style_theme: str = "default"
    layout_type: LayoutType = LayoutType.GRID
    widgets: List[WidgetConfig] = field(default_factory=list)
    menus: List[Dict[str, Any]] = field(default_factory=list)
    toolbars: List[Dict[str, Any]] = field(default_factory=list)
    statusbar: Optional[Dict[str, Any]] = None
    styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    commands: Dict[str, Callable] = field(default_factory=dict)
    validators: Dict[str, Callable] = field(default_factory=dict)
    on_init: Optional[Callable] = None
    on_close: Optional[Callable] = None

class WidgetFactory(Protocol):
    """Protocol for widget factories"""
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: 'ModularUIManager') -> tk.Widget: ...

# ============================================================================
# Built-in Widget Factories
# ============================================================================

class StandardWidgetFactory:
    """Factory for standard tkinter widgets"""
    
    def create_widget(self, parent: tk.Widget, config: WidgetConfig, 
                     ui_manager: 'ModularUIManager') -> tk.Widget:
        """Create a standard widget"""
        widget_type = config.widget_type

        # Support for custom string widget types (e.g., 'scrollable_frame')
        if isinstance(widget_type, str):
            if widget_type == 'scrollable_frame':
                return self._create_scrollable_frame(parent, config, ui_manager)
            # Custom widget type
            return self._create_custom_widget(parent, config, ui_manager)

        # Standard widget creation
        widget_map = {
            WidgetType.LABEL: self._create_label,
            WidgetType.BUTTON: self._create_button, 
            WidgetType.ENTRY: self._create_entry,
            WidgetType.TEXT: self._create_text,
            WidgetType.LISTBOX: self._create_listbox,
            WidgetType.TREEVIEW: self._create_treeview,
            WidgetType.COMBOBOX: self._create_combobox,
            WidgetType.SPINBOX: self._create_spinbox,
            WidgetType.SCALE: self._create_scale,
            WidgetType.CHECKBUTTON: self._create_checkbutton,
            WidgetType.RADIOBUTTON: self._create_radiobutton,
            WidgetType.FRAME: self._create_frame,
            WidgetType.LABELFRAME: self._create_labelframe,
            WidgetType.NOTEBOOK: self._create_notebook,
            WidgetType.PANEDWINDOW: self._create_panedwindow,
            WidgetType.CANVAS: self._create_canvas,
            WidgetType.PROGRESSBAR: self._create_progressbar,
            WidgetType.SEPARATOR: self._create_separator,
        }

        factory_func = widget_map.get(widget_type)
        if not factory_func:
            raise ValueError(f"Unsupported widget type: {widget_type}")

        return factory_func(parent, config, ui_manager)

    def _create_scrollable_frame(self, parent, config, ui_manager):
        # Create a frame with a vertical scrollbar and a canvas
        outer_frame = ttk.Frame(parent)
        canvas = tk.Canvas(outer_frame, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure canvas and scrollbar
        scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)

        def _on_frame_configure(event):
            # Update scrollregion to match the size of the inner frame
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", _on_frame_configure)

        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

        # Add children widgets
        for child_config in getattr(config, 'children', []):
            child_widget = ui_manager.widget_factory.create_widget(scrollable_frame, child_config, ui_manager)
            # Use pack for vertical stacking by default
            child_widget.pack(fill="x", padx=5, pady=2)

        return outer_frame
    
    def _create_label(self, parent, config, ui_manager):
        widget = ttk.Label(parent, text=config.text, **config.options)
        return widget
    
    def _create_button(self, parent, config, ui_manager):
        command = None
        if config.command:
            command = ui_manager.get_command(config.command)
        widget = ttk.Button(parent, text=config.text, command=command, **config.options)
        return widget
    
    def _create_entry(self, parent, config, ui_manager):
        variable = None
        if config.variable:
            variable = ui_manager.get_variable(config.variable)
        widget = ttk.Entry(parent, textvariable=variable, **config.options)
        if config.value:
            widget.insert(0, str(config.value))
        return widget
    
    def _create_text(self, parent, config, ui_manager):
        # Create scrolled text widget
        widget = scrolledtext.ScrolledText(parent, **config.options)
        if config.value:
            widget.insert('1.0', str(config.value))
        return widget
    
    def _create_listbox(self, parent, config, ui_manager):
        variable = None
        if config.variable:
            variable = ui_manager.get_variable(config.variable)
        widget = tk.Listbox(parent, listvariable=variable, **config.options)
        if config.value and isinstance(config.value, list):
            for item in config.value:
                widget.insert(tk.END, item)
        return widget
    
    def _create_treeview(self, parent, config, ui_manager):
        widget = ttk.Treeview(parent, **config.options)
        return widget
    
    def _create_combobox(self, parent, config, ui_manager):
        variable = None
        if config.variable:
            variable = ui_manager.get_variable(config.variable)
        widget = ttk.Combobox(parent, textvariable=variable, **config.options)
        if config.value and isinstance(config.value, list):
            widget['values'] = config.value
        return widget
    
    def _create_spinbox(self, parent, config, ui_manager):
        variable = None
        if config.variable:
            variable = ui_manager.get_variable(config.variable)
        widget = ttk.Spinbox(parent, textvariable=variable, **config.options)
        return widget
    
    def _create_scale(self, parent, config, ui_manager):
        variable = None
        if config.variable:
            variable = ui_manager.get_variable(config.variable)
        widget = ttk.Scale(parent, variable=variable, **config.options)
        return widget
    
    def _create_checkbutton(self, parent, config, ui_manager):
        variable = None
        if config.variable:
            variable = ui_manager.get_variable(config.variable)
        widget = ttk.Checkbutton(parent, text=config.text, variable=variable, **config.options)
        return widget
    
    def _create_radiobutton(self, parent, config, ui_manager):
        variable = None
        if config.variable:
            variable = ui_manager.get_variable(config.variable)
        widget = ttk.Radiobutton(parent, text=config.text, variable=variable, **config.options)
        return widget
    
    def _create_frame(self, parent, config, ui_manager):
        widget = ttk.Frame(parent, **config.options)
        return widget
    
    def _create_labelframe(self, parent, config, ui_manager):
        widget = ttk.LabelFrame(parent, text=config.text, **config.options)
        return widget
        
    def _create_notebook(self, parent, config, ui_manager):
        widget = ttk.Notebook(parent, **config.options)
        
        # Handle children as tabs
        for child_config in config.children:
            if child_config.widget_type == WidgetType.FRAME and child_config.text:
                # This is a tab frame
                tab_frame = ttk.Frame(widget)
                widget.add(tab_frame, text=child_config.text)
                
                # Create children inside the tab frame
                if child_config.children:
                    if ui_manager.current_app:
                        ui_manager.current_app._create_widgets(tab_frame, child_config.children)
        
        return widget
    
    def _create_panedwindow(self, parent, config, ui_manager):
        widget = ttk.PanedWindow(parent, **config.options)
        return widget
    
    def _create_canvas(self, parent, config, ui_manager):
        widget = tk.Canvas(parent, **config.options)
        return widget
    
    def _create_progressbar(self, parent, config, ui_manager):
        widget = ttk.Progressbar(parent, **config.options)
        return widget
    
    def _create_separator(self, parent, config, ui_manager):
        widget = ttk.Separator(parent, **config.options)
        return widget
    
    def _create_custom_widget(self, parent, config, ui_manager):
        """Create custom widget type"""
        custom_factories = ui_manager.custom_factories
        if config.widget_type in custom_factories:
            factory = custom_factories[config.widget_type]
            return factory.create_widget(parent, config, ui_manager)
        else:
            raise ValueError(f"Unknown custom widget type: {config.widget_type}")

# ============================================================================
# Layout Managers  
# ============================================================================

class LayoutManager:
    """Manages widget layout"""
    
    def apply_layout(self, widget: tk.Widget, config: WidgetConfig, 
                    layout_type: LayoutType = LayoutType.GRID) -> None:
        """Apply layout to widget"""
        layout_config = config.layout
        
        if layout_type == LayoutType.GRID:
            self._apply_grid_layout(widget, layout_config)
        elif layout_type == LayoutType.PACK:
            self._apply_pack_layout(widget, layout_config)
        elif layout_type == LayoutType.PLACE:
            self._apply_place_layout(widget, layout_config)
    
    def _apply_grid_layout(self, widget, config):
        """Apply grid layout"""
        defaults = {'sticky': 'ew', 'padx': 5, 'pady': 5}
        grid_config = {**defaults, **config}
        widget.grid(**grid_config)
    
    def _apply_pack_layout(self, widget, config):
        """Apply pack layout"""
        defaults = {'fill': 'x', 'padx': 5, 'pady': 5}
        pack_config = {**defaults, **config}
        widget.pack(**pack_config)
    
    def _apply_place_layout(self, widget, config):
        """Apply place layout"""
        widget.place(**config)

# ============================================================================
# Main Modular UI Manager
# ============================================================================

class ModularUIManager(AsyncInitializable, AsyncShutdownable):
    """
    Main UI manager for creating modular applications
    """
    
    def __init__(self, service_container: ServiceContainer):
        self.service_container = service_container
        self.event_bus: Optional[EventBus] = None
        
        # UI components
        self.root: Optional[tk.Tk] = None
        self.widgets: Dict[str, tk.Widget] = {}
        self.variables: Dict[str, tk.Variable] = {}
        self.commands: Dict[str, Callable] = {}
        self.validators: Dict[str, Callable] = {}
        
        # Current application reference
        self.current_app: Optional['ModularApplication'] = None
        
        # Factories and managers
        self.widget_factory = StandardWidgetFactory()
        self.custom_factories: Dict[str, WidgetFactory] = {}
        self.layout_manager = LayoutManager()
        
        # Configuration
        self.ui_definition: Optional[UIDefinition] = None
        self.style = None
        
        # Threading
        self.ui_thread: Optional[threading.Thread] = None
        self.ui_running = False
        self.ui_ready = threading.Event()  # Use threading.Event for sync bridge
        self._shutdown_requested = False
        logger.info("ModularUIManager initialized")
    
    async def initialize_async(self) -> None:
        """Initialize the UI system"""
        logger.info("Initializing modular UI system...")
        
        # Get event bus
        self.event_bus = await self.service_container.get_service(EventBus)
        
        logger.info("Modular UI system initialized")
    
    async def shutdown_async(self) -> None:
        """Shutdown UI system (async context)"""
        logger.info("Shutting down modular UI system...")
        self._shutdown_requested = True
        self.ui_running = False
        if self.root:
            try:
                self.root.after(0, self.root.quit)
            except Exception:
                pass
        if self.ui_thread and self.ui_thread.is_alive():
            self.ui_thread.join(timeout=5.0)
        logger.info("Modular UI system shutdown complete")
    
    def register_custom_factory(self, widget_type: str, factory: WidgetFactory) -> None:
        """Register a custom widget factory"""
        self.custom_factories[widget_type] = factory
        logger.debug(f"Registered custom widget factory: {widget_type}")
    
    def create_application(self, ui_definition: UIDefinition) -> 'ModularApplication':
        """Create a modular application"""
        app = ModularApplication(self, ui_definition)
        self.current_app = app
        return app
    
    def load_ui_from_json(self, json_path: str) -> UIDefinition:
        """Load UI definition from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        return self._dict_to_ui_definition(data)
    
    def load_ui_from_dict(self, data: Dict[str, Any]) -> UIDefinition:
        """Load UI definition from dictionary"""
        return self._dict_to_ui_definition(data)
    
    def _dict_to_ui_definition(self, data: Dict[str, Any]) -> UIDefinition:
        """Convert dictionary to UIDefinition"""
        # This would include comprehensive conversion logic
        # For now, a simplified version
        return UIDefinition(
            title=data.get('title', 'Modular Application'),
            geometry=data.get('geometry', '800x600'),
            widgets=self._convert_widgets(data.get('widgets', [])),
            # Add other fields as needed
        )
    
    def _convert_widgets(self, widgets_data: List[Dict]) -> List[WidgetConfig]:
        """Convert widget data to WidgetConfig objects"""
        configs = []
        for widget_data in widgets_data:
            config = WidgetConfig(
                widget_type=WidgetType(widget_data['type']) if widget_data['type'] in [e.value for e in WidgetType] else widget_data['type'],
                text=widget_data.get('text', ''),
                value=widget_data.get('value'),
                command=widget_data.get('command'),
                variable=widget_data.get('variable'),
                options=widget_data.get('options', {}),
                layout=widget_data.get('layout', {}),
                children=self._convert_widgets(widget_data.get('children', []))
            )
            configs.append(config)
        return configs
    
    def get_variable(self, name: str) -> tk.Variable:
        """Get or create a tkinter variable"""
        if name not in self.variables:
            self.variables[name] = tk.StringVar()
        return self.variables[name]
    
    def get_command(self, name: str) -> Optional[Callable]:
        """Get a command by name"""
        return self.commands.get(name)
    
    def set_command(self, name: str, command: Callable) -> None:
        """Set a command"""
        self.commands[name] = command
    
    def get_widget(self, name: str) -> Optional[tk.Widget]:
        """Get a widget by name"""
        return self.widgets.get(name)
    
    def launch_in_thread(self, ui_definition: UIDefinition) -> 'ModularApplication':
        """Launch the modular UI in a background thread (async-to-sync bridge)"""
        self.ui_definition = ui_definition
        self.ui_running = True
        self.ui_ready.clear()
        app_holder = {}
        def _thread_target():
            app = ModularApplication(self, ui_definition)
            app_holder['app'] = app
            self.ui_ready.set()  # Signal ready after app is created
            app.run()
            self.ui_running = False
        self.ui_thread = threading.Thread(target=_thread_target, daemon=True)
        self.ui_thread.start()
        self.ui_ready.wait()  # Block until UI is ready
        return app_holder['app']

# ============================================================================
# Modular Application Class
# ============================================================================

class ModularApplication:
    """A complete modular application"""
    
    def __init__(self, ui_manager: ModularUIManager, ui_definition: UIDefinition):
        self.ui_manager = ui_manager
        self.ui_definition = ui_definition
        self.root: Optional[tk.Tk] = None
        self.running = False
        
    def build_ui(self) -> None:
        """Build the UI from definition"""
        # Create root window
        self.root = tk.Tk()
        self.root.title(self.ui_definition.title)
        self.root.geometry(self.ui_definition.geometry)
        
        if self.ui_definition.icon:
            try:
                self.root.iconbitmap(self.ui_definition.icon)
            except Exception:
                logger.warning(f"Could not load icon: {self.ui_definition.icon}")
        
        # Setup styling
        self._setup_styling()
        
        # Register commands
        for name, command in self.ui_definition.commands.items():
            self.ui_manager.set_command(name, command)
        
        # Initialize variables
        for name, value in self.ui_definition.variables.items():
            var = self.ui_manager.get_variable(name)
            var.set(value)
        
        # Create widgets
        self._create_widgets(self.root, self.ui_definition.widgets)
        
        # Setup menus
        self._setup_menus()
        
        # Setup toolbars
        self._setup_toolbars()
        
        # Setup statusbar
        self._setup_statusbar()
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Call initialization callback
        if self.ui_definition.on_init:
            self.ui_definition.on_init(self)
    
    def _setup_styling(self) -> None:
        """Setup UI styling"""
        self.ui_manager.style = ttk.Style()
        
        # Apply theme
        try:
            self.ui_manager.style.theme_use(self.ui_definition.style_theme)
        except Exception:
            logger.warning(f"Could not apply theme: {self.ui_definition.style_theme}")
        
        # Apply custom styles
        for style_name, style_config in self.ui_definition.styles.items():
            self.ui_manager.style.configure(style_name, **style_config)
    
    def _create_widgets(self, parent: tk.Widget, widgets: List[WidgetConfig], 
                       widget_id_prefix: str = "") -> None:
        """Create widgets recursively"""
        for i, widget_config in enumerate(widgets):
            widget_id = f"{widget_id_prefix}widget_{i}"
            
            # Create the widget
            widget = self.ui_manager.widget_factory.create_widget(
                parent, widget_config, self.ui_manager
            )
            
            # Store widget reference
            self.ui_manager.widgets[widget_id] = widget
            
            # Apply styling
            if widget_config.style:
                try:
                    widget.configure(**widget_config.style)
                except Exception as e:
                    logger.warning(f"Could not apply style to {widget_id}: {e}")
            
            # Apply layout
            self.ui_manager.layout_manager.apply_layout(
                widget, widget_config, self.ui_definition.layout_type
            )
            
            # Add tooltip
            if widget_config.tooltip:
                self._add_tooltip(widget, widget_config.tooltip)
            
            # Set enabled/visible state
            if not widget_config.enabled:
                widget.configure(state='disabled')
            if not widget_config.visible:
                widget.grid_remove()  # or pack_forget() depending on layout
            
            # Bind events
            for event, command_name in widget_config.bindings.items():
                command = self.ui_manager.get_command(command_name)
                if command:
                    widget.bind(event, command)
            
            # Create children
            if widget_config.children:
                self._create_widgets(widget, widget_config.children, f"{widget_id}_")
    
    def _setup_menus(self) -> None:
        """Setup application menus"""
        if not self.ui_definition.menus:
            return
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        for menu_config in self.ui_definition.menus:
            self._create_menu(menubar, menu_config)
    
    def _create_menu(self, parent: tk.Menu, config: Dict[str, Any]) -> None:
        """Create a menu"""
        menu = tk.Menu(parent, tearoff=0)
        parent.add_cascade(label=config['label'], menu=menu)
        
        for item in config.get('items', []):
            if item.get('separator'):
                menu.add_separator()
            else:
                command = None
                if 'command' in item:
                    command = self.ui_manager.get_command(item['command'])
                menu.add_command(
                    label=item['label'],
                    command=command,
                    accelerator=item.get('accelerator')
                )
    
    def _setup_toolbars(self) -> None:
        """Setup application toolbars"""
        # Implementation for toolbars
        pass
    
    def _setup_statusbar(self) -> None:
        """Setup application statusbar"""
        if not self.ui_definition.statusbar:
            return
        
        statusbar = ttk.Frame(self.root)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = ttk.Label(statusbar, text="Ready")
        status_label.pack(side=tk.LEFT)
        
        self.ui_manager.widgets['statusbar'] = status_label
    
    def _add_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Add tooltip to widget"""
        # Simple tooltip implementation
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _on_window_close(self) -> None:
        """Handle window close event"""
        if self.ui_definition.on_close:
            if self.ui_definition.on_close(self):
                return  # Cancel close
        
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self) -> None:
        """Run the application (mainloop, blocking)"""
        if not self.root:
            self.build_ui()
        self.running = True
        logger.info(f"Starting modular application: {self.ui_definition.title}")
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in modular application mainloop: {e}")
        logger.info("Modular application ended")
    
    def show(self) -> None:
        """Show the application window"""
        if not self.root:
            self.build_ui()
        self.root.deiconify()
    
    def hide(self) -> None:
        """Hide the application window"""
        if self.root:
            self.root.withdraw()
    
    def destroy(self) -> None:
        """Destroy the application"""
        if self.root:
            self.root.destroy()
            self.root = None
