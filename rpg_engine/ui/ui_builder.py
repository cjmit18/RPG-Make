"""
UI Builder - Fluent API for easy UI construction
Provides builder patterns and helper functions for simple UI creation

Examples:
    # Simple window with buttons
    app = UIBuilder("My App") \
        .with_size(800, 600) \
        .add_button("Click Me", command="handle_click") \
        .add_label("Hello World") \
        .build()
    
    # Complex form
    form = FormBuilder("User Registration") \
        .add_text_field("username", "Username:") \
        .add_password_field("password", "Password:") \
        .add_dropdown("country", "Country:", ["USA", "Canada", "UK"]) \
        .add_submit_button("Register", "handle_register") \
        .build()
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, List, Union
import logging
from dataclasses import dataclass
from enum import Enum

from .modular_ui_system import (
    UIDefinition, WidgetConfig, WidgetType, LayoutType, 
    ModularUIManager, ModularApplication
)

logger = logging.getLogger(__name__)

# ============================================================================
# Fluent UI Builder
# ============================================================================

class UIBuilder:
    def add_scrollable_frame(self, children: Optional[List[WidgetConfig]] = None, **options) -> 'UIBuilder':
        """Add a scrollable frame widget (vertical scrolling). Children should be a list of WidgetConfig objects."""
        config = WidgetConfig(
            widget_type='scrollable_frame',
            children=children or [],
            options=options
        )
        self._add_widget(config)
        return self
    """Fluent API for building UIs"""
    
    def __init__(self, title: str = "Application"):
        self.ui_def = UIDefinition(title=title)
        self._current_container_stack: List[WidgetConfig] = []
    
    def with_size(self, width: int, height: int) -> 'UIBuilder':
        """Set window size"""
        self.ui_def.geometry = f"{width}x{height}"
        return self
    
    def with_icon(self, icon_path: str) -> 'UIBuilder':
        """Set window icon"""
        self.ui_def.icon = icon_path
        return self
    
    def with_theme(self, theme: str) -> 'UIBuilder':
        """Set UI theme"""
        self.ui_def.style_theme = theme
        return self
    
    def with_layout(self, layout_type: LayoutType) -> 'UIBuilder':
        """Set layout type"""
        self.ui_def.layout_type = layout_type
        return self
    
    def with_variable(self, name: str, value: Any) -> 'UIBuilder':
        """Add a variable"""
        self.ui_def.variables[name] = value
        return self
    
    def with_command(self, name: str, command: Callable) -> 'UIBuilder':
        """Add a command"""
        self.ui_def.commands[name] = command
        return self
    
    def with_style(self, style_name: str, **style_props) -> 'UIBuilder':
        """Add a custom style"""
        self.ui_def.styles[style_name] = style_props
        return self
    
    def on_init(self, callback: Callable) -> 'UIBuilder':
        """Set initialization callback"""
        self.ui_def.on_init = callback
        return self
    
    def on_close(self, callback: Callable) -> 'UIBuilder':
        """Set close callback"""
        self.ui_def.on_close = callback
        return self
    
    # Widget creation methods
    def add_label(self, text: str, **options) -> 'UIBuilder':
        """Add a label"""
        config = WidgetConfig(
            widget_type=WidgetType.LABEL,
            text=text,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_button(self, text: str, command: Optional[str] = None, **options) -> 'UIBuilder':
        """Add a button"""
        config = WidgetConfig(
            widget_type=WidgetType.BUTTON,
            text=text,
            command=command,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_entry(self, variable: Optional[str] = None, value: str = "", **options) -> 'UIBuilder':
        """Add an entry field"""
        config = WidgetConfig(
            widget_type=WidgetType.ENTRY,
            variable=variable,
            value=value,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_text(self, value: str = "", **options) -> 'UIBuilder':
        """Add a text area"""
        config = WidgetConfig(
            widget_type=WidgetType.TEXT,
            value=value,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_listbox(self, items: Optional[List[str]] = None, variable: Optional[str] = None, **options) -> 'UIBuilder':
        """Add a listbox"""
        config = WidgetConfig(
            widget_type=WidgetType.LISTBOX,
            value=items or [],
            variable=variable,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_combobox(self, values: Optional[List[str]] = None, variable: Optional[str] = None, **options) -> 'UIBuilder':
        """Add a combobox"""
        config = WidgetConfig(
            widget_type=WidgetType.COMBOBOX,
            value=values or [],
            variable=variable,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_checkbutton(self, text: str, variable: Optional[str] = None, **options) -> 'UIBuilder':
        """Add a checkbutton"""
        config = WidgetConfig(
            widget_type=WidgetType.CHECKBUTTON,
            text=text,
            variable=variable,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_radiobutton(self, text: str, variable: Optional[str] = None, value: Any = None, **options) -> 'UIBuilder':
        """Add a radiobutton"""
        config = WidgetConfig(
            widget_type=WidgetType.RADIOBUTTON,
            text=text,
            variable=variable,
            value=value,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_scale(self, from_: float = 0, to: float = 100, variable: Optional[str] = None, **options) -> 'UIBuilder':
        """Add a scale"""
        options['from_'] = from_
        options['to'] = to
        config = WidgetConfig(
            widget_type=WidgetType.SCALE,
            variable=variable,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_progressbar(self, **options) -> 'UIBuilder':
        """Add a progress bar"""
        config = WidgetConfig(
            widget_type=WidgetType.PROGRESSBAR,
            options=options
        )
        self._add_widget(config)
        return self
    
    def add_separator(self, **options) -> 'UIBuilder':
        """Add a separator"""
        config = WidgetConfig(
            widget_type=WidgetType.SEPARATOR,
            options=options
        )
        self._add_widget(config)
        return self
    
    # Container methods
    def begin_frame(self, text: str = "", **options) -> 'UIBuilder':
        """Begin a frame container"""
        config = WidgetConfig(
            widget_type=WidgetType.LABELFRAME if text else WidgetType.FRAME,
            text=text,
            options=options
        )
        self._begin_container(config)
        return self
    
    def begin_notebook(self, **options) -> 'UIBuilder':
        """Begin a notebook container"""
        config = WidgetConfig(
            widget_type=WidgetType.NOTEBOOK,
            options=options
        )
        self._begin_container(config)
        return self
    
    def add_notebook(self, **options) -> 'UIBuilder':
        """Add a notebook widget (for backwards compatibility)"""
        return self.begin_notebook(**options)
    
    def begin_tab(self, title: str, **options) -> 'UIBuilder':
        """Begin a tab in the current notebook"""
        if not self._current_container_stack or self._current_container_stack[-1].widget_type != WidgetType.NOTEBOOK:
            raise ValueError("begin_tab() can only be called inside a notebook container")
        
        # Create a frame for the tab content
        config = WidgetConfig(
            widget_type=WidgetType.FRAME,
            text=title,  # Store tab title in text field
            options=options
        )
        self._begin_container(config)
        return self
    
    def end_tab(self) -> 'UIBuilder':
        """End current tab (same as end_container)"""
        return self.end_container()
    
    def begin_paned_window(self, **options) -> 'UIBuilder':
        """Begin a paned window container"""
        config = WidgetConfig(
            widget_type=WidgetType.PANEDWINDOW,
            options=options
        )
        self._begin_container(config)
        return self
    
    def end_container(self) -> 'UIBuilder':
        """End current container"""
        if self._current_container_stack:
            container = self._current_container_stack.pop()
            self._add_widget(container)
        return self
    
    # Layout methods
    def with_grid_layout(self, row: int, column: int, **layout_options) -> 'UIBuilder':
        """Set grid layout for next widget"""
        layout_options['row'] = row
        layout_options['column'] = column
        if self._current_container_stack:
            # Apply to current container
            self._current_container_stack[-1].layout.update(layout_options)
        return self
    
    def with_pack_layout(self, **layout_options) -> 'UIBuilder':
        """Set pack layout for next widget"""
        if self._current_container_stack:
            self._current_container_stack[-1].layout.update(layout_options)
        return self
    
    # Menu methods
    def add_menu(self, label: str, items: List[Dict[str, Any]]) -> 'UIBuilder':
        """Add a menu"""
        self.ui_def.menus.append({
            'label': label,
            'items': items
        })
        return self
    
    def add_statusbar(self, **options) -> 'UIBuilder':
        """Add a status bar"""
        self.ui_def.statusbar = options
        return self
    
    def _add_widget(self, config: WidgetConfig) -> None:
        """Add widget to current container or root"""
        if self._current_container_stack:
            self._current_container_stack[-1].children.append(config)
        else:
            self.ui_def.widgets.append(config)
    
    def _begin_container(self, config: WidgetConfig) -> None:
        """Begin a new container"""
        self._current_container_stack.append(config)
    
    def build(self) -> UIDefinition:
        """Build and return the UI definition"""
        # Finalize any open containers
        while self._current_container_stack:
            self.end_container()
        
        return self.ui_def

# ============================================================================
# Specialized Builders
# ============================================================================

class FormBuilder:
    """Builder for form-based UIs"""
    
    def __init__(self, title: str = "Form"):
        self.builder = UIBuilder(title)
        self.row_count = 0
    
    def add_text_field(self, name: str, label: str, required: bool = False, **options) -> 'FormBuilder':
        """Add a text input field"""
        # Add label
        self.builder.add_label(f"{label}{'*' if required else ''}")
        self.builder.with_grid_layout(self.row_count, 0, sticky='w')
        
        # Add entry
        self.builder.add_entry(variable=name, **options)
        self.builder.with_grid_layout(self.row_count, 1, sticky='ew')
        
        self.row_count += 1
        return self
    
    def add_password_field(self, name: str, label: str, **options) -> 'FormBuilder':
        """Add a password field"""
        options['show'] = '*'
        return self.add_text_field(name, label, **options)
    
    def add_dropdown(self, name: str, label: str, values: List[str], **options) -> 'FormBuilder':
        """Add a dropdown field"""
        # Add label
        self.builder.add_label(label)
        self.builder.with_grid_layout(self.row_count, 0, sticky='w')
        
        # Add combobox
        self.builder.add_combobox(values=values, variable=name, **options)
        self.builder.with_grid_layout(self.row_count, 1, sticky='ew')
        
        self.row_count += 1
        return self
    
    def add_checkbox_field(self, name: str, label: str, **options) -> 'FormBuilder':
        """Add a checkbox field"""
        self.builder.add_checkbutton(label, variable=name, **options)
        self.builder.with_grid_layout(self.row_count, 0, columnspan=2, sticky='w')
        
        self.row_count += 1
        return self
    
    def add_text_area(self, name: str, label: str, rows: int = 5, **options) -> 'FormBuilder':
        """Add a text area"""
        # Add label
        self.builder.add_label(label)
        self.builder.with_grid_layout(self.row_count, 0, sticky='nw')
        
        # Add text area
        options['height'] = rows
        self.builder.add_text(**options)
        self.builder.with_grid_layout(self.row_count, 1, sticky='ew')
        
        self.row_count += 1
        return self
    
    def add_submit_button(self, text: str = "Submit", command: Optional[str] = None, **options) -> 'FormBuilder':
        """Add a submit button"""
        self.builder.add_button(text, command=command, **options)
        self.builder.with_grid_layout(self.row_count, 1, sticky='e')
        
        self.row_count += 1
        return self
    
    def add_button_row(self, buttons: List[Dict[str, Any]]) -> 'FormBuilder':
        """Add a row of buttons"""
        self.builder.begin_frame()
        
        for i, button_config in enumerate(buttons):
            self.builder.add_button(
                button_config['text'],
                command=button_config.get('command'),
                **button_config.get('options', {})
            )
            self.builder.with_pack_layout(side='left', padx=5)
        
        self.builder.end_container()
        self.builder.with_grid_layout(self.row_count, 0, columnspan=2, sticky='ew')
        
        self.row_count += 1
        return self
    
    def build(self) -> UIDefinition:
        """Build the form"""
        return self.builder.build()

class DialogBuilder:
    """Builder for dialog windows"""
    
    def __init__(self, title: str = "Dialog"):
        self.builder = UIBuilder(title)
        self.builder.with_size(400, 300)
    
    def with_message(self, message: str) -> 'DialogBuilder':
        """Add a message"""
        self.builder.add_label(message, wraplength=350, justify='left')
        self.builder.with_pack_layout(padx=20, pady=20, fill='x')
        return self
    
    def with_input(self, label: str, variable: str = "user_input") -> 'DialogBuilder':
        """Add an input field"""
        self.builder.add_label(label)
        self.builder.with_pack_layout(padx=20, pady=(0, 5), anchor='w')
        
        self.builder.add_entry(variable=variable)
        self.builder.with_pack_layout(padx=20, pady=(0, 20), fill='x')
        return self
    
    def with_buttons(self, buttons: List[Dict[str, Any]]) -> 'DialogBuilder':
        """Add dialog buttons"""
        self.builder.begin_frame()
        
        for button_config in buttons:
            self.builder.add_button(
                button_config['text'],
                command=button_config.get('command'),
                **button_config.get('options', {})
            )
            self.builder.with_pack_layout(side='right', padx=5)
        
        self.builder.end_container()
        self.builder.with_pack_layout(pady=20, anchor='e', padx=20)
        return self
    
    def build(self) -> UIDefinition:
        """Build the dialog"""
        return self.builder.build()

class MenuBuilder:
    """Builder for menu systems"""
    
    def __init__(self):
        self.menus: List[Dict[str, Any]] = []
    
    def add_menu(self, label: str) -> 'MenuItemBuilder':
        """Add a new menu"""
        return MenuItemBuilder(self, label)
    
    def build(self) -> List[Dict[str, Any]]:
        """Build the menu structure"""
        return self.menus

class MenuItemBuilder:
    """Builder for menu items"""
    
    def __init__(self, menu_builder: MenuBuilder, menu_label: str):
        self.menu_builder = menu_builder
        self.menu_label = menu_label
        self.items: List[Dict[str, Any]] = []
    
    def add_item(self, label: str, command: Optional[str] = None, 
                accelerator: Optional[str] = None) -> 'MenuItemBuilder':
        """Add a menu item"""
        item = {'label': label}
        if command:
            item['command'] = command
        if accelerator:
            item['accelerator'] = accelerator
        
        self.items.append(item)
        return self
    
    def add_separator(self) -> 'MenuItemBuilder':
        """Add a menu separator"""
        self.items.append({'separator': True})
        return self
    
    def end_menu(self) -> MenuBuilder:
        """End menu and return to menu builder"""
        self.menu_builder.menus.append({
            'label': self.menu_label,
            'items': self.items
        })
        return self.menu_builder

# ============================================================================
# Quick Creation Functions
# ============================================================================

def create_simple_window(title: str, width: int = 800, height: int = 600) -> UIBuilder:
    """Create a simple window"""
    return UIBuilder(title).with_size(width, height)

def create_form_dialog(title: str, fields: List[Dict[str, Any]]) -> UIDefinition:
    """Create a form dialog quickly"""
    form = FormBuilder(title)
    
    for field in fields:
        field_type = field.get('type', 'text')
        name = field['name']
        label = field['label']
        
        if field_type == 'text':
            form.add_text_field(name, label, **field.get('options', {}))
        elif field_type == 'password':
            form.add_password_field(name, label, **field.get('options', {}))
        elif field_type == 'dropdown':
            form.add_dropdown(name, label, field['values'], **field.get('options', {}))
        elif field_type == 'checkbox': 
            form.add_checkbox_field(name, label, **field.get('options', {}))
        elif field_type == 'textarea':
            form.add_text_area(name, label, **field.get('options', {}))
    
    # Add default submit button
    form.add_submit_button()
    
    return form.build()

def create_message_dialog(title: str, message: str, buttons: Optional[List[str]] = None) -> UIDefinition:
    """Create a message dialog"""
    if buttons is None:
        buttons = ['OK']
    
    dialog = DialogBuilder(title).with_message(message)
    
    button_configs = []
    for button_text in buttons:
        button_configs.append({
            'text': button_text,
            'command': f'handle_{button_text.lower()}'
        })
    
    dialog.with_buttons(button_configs)
    return dialog.build()

def create_confirmation_dialog(title: str, message: str) -> UIDefinition:
    """Create a yes/no confirmation dialog"""
    return create_message_dialog(title, message, ['Yes', 'No'])

def create_input_dialog(title: str, prompt: str, variable: str = "user_input") -> UIDefinition:
    """Create an input dialog"""
    return DialogBuilder(title) \
        .with_message(prompt) \
        .with_input("", variable) \
        .with_buttons([
            {'text': 'OK', 'command': 'handle_ok'},
            {'text': 'Cancel', 'command': 'handle_cancel'}
        ]) \
        .build()

# ============================================================================
# Template System
# ============================================================================

class UITemplate:
    """Base class for UI templates"""
    
    @staticmethod
    def create_crud_interface(entity_name: str) -> UIDefinition:
        """Create a CRUD interface template"""
        return UIBuilder(f"{entity_name} Management") \
            .with_size(1000, 700) \
            .begin_paned_window(orient='horizontal') \
                .begin_frame("Items") \
                    .add_listbox(variable=f"{entity_name.lower()}_list") \
                    .with_pack_layout(fill='both', expand=True) \
                .end_container() \
                .begin_frame("Details") \
                    .add_label("Name:") \
                    .add_entry(variable="item_name") \
                    .add_label("Description:") \
                    .add_text(variable="item_description") \
                    .begin_frame() \
                        .add_button("Save", command="save_item") \
                        .add_button("Delete", command="delete_item") \
                        .add_button("New", command="new_item") \
                    .end_container() \
                .end_container() \
            .end_container() \
            .build()
    
    @staticmethod
    def create_settings_dialog() -> UIDefinition:
        """Create a settings dialog template"""
        return UIBuilder("Settings") \
            .with_size(500, 400) \
            .begin_notebook() \
                .begin_frame("General") \
                    .add_checkbox_field("auto_save", "Auto-save changes") \
                    .add_checkbox_field("show_tooltips", "Show tooltips") \
                    .add_dropdown("theme", "Theme:", ["Default", "Dark", "Light"]) \
                .end_container() \
                .begin_frame("Advanced") \
                    .add_text_field("log_level", "Log Level:") \
                    .add_checkbox_field("debug_mode", "Debug mode") \
                .end_container() \
            .end_container() \
            .add_button_row([
                {'text': 'OK', 'command': 'save_settings'},
                {'text': 'Cancel', 'command': 'cancel_settings'},
                {'text': 'Apply', 'command': 'apply_settings'}
            ]) \
            .build()
    
    @staticmethod 
    def create_data_viewer(title: str, columns: List[str]) -> UIDefinition:
        """Create a data viewer template"""
        builder = UIBuilder(title).with_size(800, 600)
        
        # Add toolbar
        builder.begin_frame() \
            .add_button("Refresh", command="refresh_data") \
            .add_button("Export", command="export_data") \
            .add_button("Filter", command="show_filter") \
            .with_pack_layout(side='left', padx=2) \
        .end_container() \
        .with_pack_layout(fill='x', pady=(0, 10))
        
        # Add treeview for data
        builder.add_treeview(columns=columns, show='headings') \
            .with_pack_layout(fill='both', expand=True)
        
        return builder.build()
