"""
Tabbed Interface
================

A comprehensive tabbed interface system for organizing application content
with support for dynamic tab management and content providers.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Protocol
from dataclasses import dataclass


@dataclass
class TabConfig:
    """Configuration for a single tab."""
    tab_id: str
    title: str
    tooltip: Optional[str] = None
    closable: bool = False


class TabContentProvider(Protocol):
    """Protocol for tab content providers."""
    
    def create_content(self, parent: tk.Widget) -> tk.Widget:
        """Create the tab content."""
        ...
    
    def refresh_content(self) -> None:
        """Refresh the tab content."""
        ...
    
    def on_tab_selected(self) -> None:
        """Called when the tab is selected."""
        ...
    
    def on_tab_deselected(self) -> None:
        """Called when the tab is deselected."""
        ...
    
    def can_close(self) -> bool:
        """Return whether the tab can be closed."""
        ...


class TabbedInterface:
    """
    A sophisticated tabbed interface with dynamic content management.
    
    Supports:
    - Dynamic tab addition/removal
    - Content providers for flexible tab content
    - Tab state management
    - Event callbacks
    """
    
    def __init__(self, parent: tk.Widget):
        """Initialize the tabbed interface."""
        self.parent = parent
        self.tabs: Dict[str, Dict[str, Any]] = {}
        self.current_tab: Optional[str] = None
        
        # Create notebook widget
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def add_tab(self, config: TabConfig, provider: TabContentProvider) -> bool:
        """
        Add a new tab to the interface.
        
        Args:
            config: Tab configuration
            provider: Content provider for the tab
            
        Returns:
            True if tab was added successfully
        """
        try:
            if config.tab_id in self.tabs:
                return False  # Tab already exists
            
            # Create tab frame
            tab_frame = ttk.Frame(self.notebook)
            
            # Create content using provider
            content_widget = provider.create_content(tab_frame)
            
            # Add to notebook
            self.notebook.add(tab_frame, text=config.title)
            
            # Store tab info
            self.tabs[config.tab_id] = {
                'config': config,
                'provider': provider,
                'frame': tab_frame,
                'content': content_widget
            }
            
            # Set tooltip if provided
            if config.tooltip:
                self._set_tab_tooltip(tab_frame, config.tooltip)
            
            return True
            
        except Exception as e:
            print(f"Error adding tab {config.tab_id}: {e}")
            return False
    
    def remove_tab(self, tab_id: str) -> bool:
        """
        Remove a tab from the interface.
        
        Args:
            tab_id: ID of the tab to remove
            
        Returns:
            True if tab was removed successfully
        """
        if tab_id not in self.tabs:
            return False
        
        tab_info = self.tabs[tab_id]
        
        # Check if tab can be closed
        if not tab_info['provider'].can_close():
            return False
        
        # Remove from notebook
        tab_frame = tab_info['frame']
        for i, child in enumerate(self.notebook.tabs()):
            if self.notebook.nametowidget(child) == tab_frame:
                self.notebook.forget(i)
                break
        
        # Clean up
        del self.tabs[tab_id]
        
        # Update current tab if necessary
        if self.current_tab == tab_id:
            self.current_tab = None
            if self.tabs:
                # Select first available tab
                first_tab_id = next(iter(self.tabs))
                self.select_tab(first_tab_id)
        
        return True
    
    def select_tab(self, tab_id: str) -> bool:
        """
        Select a specific tab.
        
        Args:
            tab_id: ID of the tab to select
            
        Returns:
            True if tab was selected successfully
        """
        if tab_id not in self.tabs:
            return False
        
        tab_info = self.tabs[tab_id]
        tab_frame = tab_info['frame']
        
        # Find tab index and select it
        for i, child in enumerate(self.notebook.tabs()):
            if self.notebook.nametowidget(child) == tab_frame:
                self.notebook.select(i)
                return True
        
        return False
    
    def get_current_tab(self) -> Optional[str]:
        """Get the currently selected tab ID."""
        return self.current_tab
    
    def get_tab_count(self) -> int:
        """Get the number of tabs."""
        return len(self.tabs)
    
    def refresh_active_tab(self) -> None:
        """Refresh the currently active tab."""
        if self.current_tab and self.current_tab in self.tabs:
            provider = self.tabs[self.current_tab]['provider']
            provider.refresh_content()
    
    def refresh_tab(self, tab_id: str) -> bool:
        """
        Refresh a specific tab.
        
        Args:
            tab_id: ID of the tab to refresh
            
        Returns:
            True if tab was refreshed successfully
        """
        if tab_id not in self.tabs:
            return False
        
        provider = self.tabs[tab_id]['provider']
        provider.refresh_content()
        return True
    
    def _on_tab_changed(self, event) -> None:
        """Handle tab selection change."""
        try:
            # Get selected tab
            selected = self.notebook.select()
            if not selected:
                return
            
            selected_widget = self.notebook.nametowidget(selected)
            
            # Find corresponding tab ID
            new_tab_id = None
            for tab_id, tab_info in self.tabs.items():
                if tab_info['frame'] == selected_widget:
                    new_tab_id = tab_id
                    break
            
            if not new_tab_id:
                return
            
            # Call deselection callback for previous tab
            if self.current_tab and self.current_tab in self.tabs:
                old_provider = self.tabs[self.current_tab]['provider']
                old_provider.on_tab_deselected()
            
            # Update current tab
            self.current_tab = new_tab_id
            
            # Call selection callback for new tab
            new_provider = self.tabs[new_tab_id]['provider']
            new_provider.on_tab_selected()
            
        except Exception as e:
            print(f"Error in tab change handler: {e}")
    
    def _set_tab_tooltip(self, tab_frame: tk.Widget, tooltip: str) -> None:
        """Set tooltip for a tab (basic implementation)."""
        # This is a simple tooltip implementation
        # In a full implementation, you might want a more sophisticated tooltip system
        def on_enter(event):
            # Could implement tooltip popup here
            pass
        
        def on_leave(event):
            # Could hide tooltip popup here
            pass
        
        tab_frame.bind("<Enter>", on_enter)
        tab_frame.bind("<Leave>", on_leave)
