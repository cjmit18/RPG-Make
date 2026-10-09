#!/usr/bin/env python3
"""
Dynamic Tab Manager - Advanced tab system with dynamic loading and state management
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, List
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class TabState:
    """Represents the state of a tab"""
    tab_id: str
    title: str
    icon: str = ""
    is_loaded: bool = False
    is_active: bool = False
    is_dirty: bool = False  # Has unsaved changes
    data: Dict[str, Any] = field(default_factory=dict)
    widgets: Dict[str, tk.Widget] = field(default_factory=dict)

class TabProvider(ABC):
    """Abstract base class for tab content providers"""
    
    @abstractmethod
    def get_tab_info(self) -> Dict[str, str]:
        """Return tab metadata (title, icon, description)"""
        pass
    
    @abstractmethod
    def create_content(self, parent: tk.Widget, tab_state: TabState) -> tk.Widget:
        """Create the tab content widget"""
        pass
    
    @abstractmethod
    def on_tab_activated(self, tab_state: TabState) -> None:
        """Called when tab becomes active"""
        pass
    
    @abstractmethod
    def on_tab_deactivated(self, tab_state: TabState) -> None:
        """Called when tab becomes inactive"""
        pass
    
    def on_tab_closing(self, tab_state: TabState) -> bool:
        """Called when tab is about to close. Return False to prevent closing."""
        return not tab_state.is_dirty
    
    def get_commands(self) -> Dict[str, Callable]:
        """Return tab-specific commands"""
        return {}

class DynamicTabManager:
    """Advanced tab manager with dynamic loading and state management"""
    
    def __init__(self, parent: tk.Widget, ui_manager=None):
        self.parent = parent
        self.ui_manager = ui_manager
        
        # Create notebook widget
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab management
        self.tab_providers: Dict[str, TabProvider] = {}
        self.tab_states: Dict[str, TabState] = {}
        self.active_tab_id: Optional[str] = None
        
        # Bind notebook events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Context menu for tabs
        self._setup_context_menu()
    
    def register_tab_provider(self, tab_id: str, provider: TabProvider) -> None:
        """Register a tab content provider"""
        self.tab_providers[tab_id] = provider
        
        # Create tab state
        info = provider.get_tab_info()
        tab_state = TabState(
            tab_id=tab_id,
            title=info.get('title', tab_id),
            icon=info.get('icon', ''),
        )
        self.tab_states[tab_id] = tab_state
        
        # Add tab to notebook (initially empty)
        self._add_tab_to_notebook(tab_state)
    
    def _add_tab_to_notebook(self, tab_state: TabState) -> None:
        """Add a tab to the notebook widget"""
        # Create placeholder frame
        placeholder = ttk.Frame(self.notebook)
        
        # Add tab with title and icon
        tab_title = f"{tab_state.icon} {tab_state.title}" if tab_state.icon else tab_state.title
        self.notebook.add(placeholder, text=tab_title)
        
        # Store reference
        tab_state.data['placeholder_frame'] = placeholder
    
    def _load_tab_content(self, tab_id: str) -> None:
        """Load content for a specific tab"""
        if tab_id not in self.tab_states or tab_id not in self.tab_providers:
            return
            
        tab_state = self.tab_states[tab_id]
        if tab_state.is_loaded:
            return
            
        provider = self.tab_providers[tab_id]
        placeholder = tab_state.data['placeholder_frame']
        
        try:
            # Create content
            content_widget = provider.create_content(placeholder, tab_state)
            
            # Replace placeholder with actual content
            content_widget.pack(fill="both", expand=True)
            tab_state.data['content_widget'] = content_widget
            tab_state.is_loaded = True
            
            logger.info(f"Loaded content for tab: {tab_id}")
            
        except Exception as e:
            logger.error(f"Failed to load tab content for {tab_id}: {e}")
            # Create error display
            error_label = ttk.Label(placeholder, 
                                  text=f"Error loading tab: {e}",
                                  font=("Segoe UI", 10),
                                  foreground="red")
            error_label.pack(expand=True)
    
    def _on_tab_changed(self, event) -> None:
        """Handle tab change events"""
        selected = self.notebook.select()
        if not selected:
            return
            
        # Get tab index and find corresponding tab_id
        tab_index = self.notebook.index(selected)
        tab_ids = list(self.tab_states.keys())
        
        if tab_index < len(tab_ids):
            new_tab_id = tab_ids[tab_index]
            self._switch_to_tab(new_tab_id)
    
    def _switch_to_tab(self, tab_id: str) -> None:
        """Switch to a specific tab"""
        if tab_id == self.active_tab_id:
            return
            
        # Deactivate current tab
        if self.active_tab_id:
            old_state = self.tab_states[self.active_tab_id]
            old_provider = self.tab_providers[self.active_tab_id]
            old_state.is_active = False
            old_provider.on_tab_deactivated(old_state)
        
        # Load content if needed
        self._load_tab_content(tab_id)
        
        # Activate new tab
        new_state = self.tab_states[tab_id]
        new_provider = self.tab_providers[tab_id]
        new_state.is_active = True
        new_provider.on_tab_activated(new_state)
        
        self.active_tab_id = tab_id
        logger.info(f"Switched to tab: {tab_id}")
    
    def close_tab(self, tab_id: str) -> bool:
        """Close a specific tab"""
        if tab_id not in self.tab_states:
            return False
            
        tab_state = self.tab_states[tab_id]
        provider = self.tab_providers[tab_id]
        
        # Check if tab can be closed
        if not provider.on_tab_closing(tab_state):
            return False
            
        # Find tab index
        tab_ids = list(self.tab_states.keys())
        tab_index = tab_ids.index(tab_id)
        
        # Remove from notebook
        self.notebook.forget(tab_index)
        
        # Clean up
        if tab_state.is_active:
            self.active_tab_id = None
            
        del self.tab_states[tab_id]
        del self.tab_providers[tab_id]
        
        logger.info(f"Closed tab: {tab_id}")
        return True
    
    def refresh_tab(self, tab_id: str) -> None:
        """Refresh a specific tab"""
        if tab_id not in self.tab_states:
            return
            
        tab_state = self.tab_states[tab_id]
        
        # Mark as not loaded to force reload
        tab_state.is_loaded = False
        
        # Clear content
        if 'content_widget' in tab_state.data:
            tab_state.data['content_widget'].destroy()
            del tab_state.data['content_widget']
        
        # Reload if active
        if tab_state.is_active:
            self._load_tab_content(tab_id)
    
    def mark_tab_dirty(self, tab_id: str, is_dirty: bool = True) -> None:
        """Mark a tab as having unsaved changes"""
        if tab_id in self.tab_states:
            tab_state = self.tab_states[tab_id]
            tab_state.is_dirty = is_dirty
            
            # Update tab title to show dirty state
            self._update_tab_title(tab_id)
    
    def _update_tab_title(self, tab_id: str) -> None:
        """Update tab title to reflect current state"""
        if tab_id not in self.tab_states:
            return
            
        tab_state = self.tab_states[tab_id]
        
        # Build title with icon and dirty indicator
        title = f"{tab_state.icon} {tab_state.title}" if tab_state.icon else tab_state.title
        if tab_state.is_dirty:
            title += " *"
            
        # Find tab index and update
        tab_ids = list(self.tab_states.keys())
        tab_index = tab_ids.index(tab_id)
        self.notebook.tab(tab_index, text=title)
    
    def _setup_context_menu(self) -> None:
        """Setup right-click context menu for tabs"""
        self.context_menu = tk.Menu(self.notebook, tearoff=0)
        self.context_menu.add_command(label="Refresh", command=self._context_refresh)
        self.context_menu.add_command(label="Close", command=self._context_close)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Close Others", command=self._context_close_others)
        
        # Bind right-click
        self.notebook.bind("<Button-3>", self._show_context_menu)
    
    def _show_context_menu(self, event) -> None:
        """Show context menu"""
        # Find which tab was clicked
        element = self.notebook.identify(event.x, event.y)
        if element == "label":
            index = self.notebook.index("@%d,%d" % (event.x, event.y))
            self.context_tab_index = index
            self.context_menu.post(event.x_root, event.y_root)
    
    def _context_refresh(self) -> None:
        """Context menu refresh action"""
        if hasattr(self, 'context_tab_index'):
            tab_ids = list(self.tab_states.keys())
            if self.context_tab_index < len(tab_ids):
                tab_id = tab_ids[self.context_tab_index]
                self.refresh_tab(tab_id)
    
    def _context_close(self) -> None:
        """Context menu close action"""
        if hasattr(self, 'context_tab_index'):
            tab_ids = list(self.tab_states.keys())
            if self.context_tab_index < len(tab_ids):
                tab_id = tab_ids[self.context_tab_index]
                self.close_tab(tab_id)
    
    def _context_close_others(self) -> None:
        """Context menu close others action"""
        if hasattr(self, 'context_tab_index'):
            tab_ids = list(self.tab_states.keys())
            if self.context_tab_index < len(tab_ids):
                keep_tab_id = tab_ids[self.context_tab_index]
                
                # Close all other tabs
                for tab_id in tab_ids.copy():
                    if tab_id != keep_tab_id:
                        self.close_tab(tab_id)
    
    def get_active_tab_id(self) -> Optional[str]:
        """Get the currently active tab ID"""
        return self.active_tab_id
    
    def get_tab_state(self, tab_id: str) -> Optional[TabState]:
        """Get the state of a specific tab"""
        return self.tab_states.get(tab_id)
    
    def switch_to_tab(self, tab_id: str) -> bool:
        """Programmatically switch to a tab"""
        if tab_id not in self.tab_states:
            return False
            
        tab_ids = list(self.tab_states.keys())
        tab_index = tab_ids.index(tab_id)
        self.notebook.select(tab_index)
        return True
