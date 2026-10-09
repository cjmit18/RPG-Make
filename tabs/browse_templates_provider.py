#!/usr/bin/env python3
"""
Browse Templates Tab Provider - Dynamic tab implementation for template browsing
Integrates the beautiful rich formatted view directly in the tab (no popup needed)
"""

import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
from typing import Dict, Any, Callable
import logging

from rpg_engine.ui.dynamic_tab_manager import TabProvider, TabState

logger = logging.getLogger(__name__)

class BrowseTemplatesTabProvider(TabProvider):
    """Tab provider for browsing character templates with rich formatted view"""
    
    def __init__(self, ui_manager=None):
        self.ui_manager = ui_manager
        self.templates_data = None
        self.text_widget = None
        self.use_template_button = None
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load character templates from JSON file"""
        try:
            # Try multiple possible paths
            possible_paths = [
                Path(__file__).parent.parent / "data" / "character_templates.json",
                Path(__file__).parent.parent.parent / "data" / "character_templates.json",
                Path.cwd() / "data" / "character_templates.json"
            ]
            
            data = None
            for data_path in possible_paths:
                try:
                    with open(data_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    logger.info(f"Loaded templates from: {data_path}")
                    break
                except FileNotFoundError:
                    continue
                    
            if data:
                self.templates_data = data.get("character_templates", {})
                logger.info(f"Loaded {len(self.templates_data)} character templates")
            else:
                raise FileNotFoundError("Could not find character_templates.json in any expected location")
                
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            self.templates_data = {}
    
    def get_tab_info(self) -> Dict[str, str]:
        """Return tab metadata"""
        count = len(self.templates_data) if self.templates_data else 0
        return {
            'title': f'Browse Templates ({count})',
            'icon': '📚',
            'description': 'Browse and explore character templates'
        }
    
    def create_content(self, parent: tk.Widget, tab_state: TabState) -> tk.Widget:
        """Create the enhanced tab content widget with modern styling"""
        # Main content frame with gradient-like background
        main_frame = ttk.Frame(parent)
        
        # Enhanced Header section with modern design
        header_frame = ttk.Frame(main_frame, relief="flat")
        header_frame.pack(fill="x", padx=25, pady=(25, 15))
        
        # Title with enhanced styling
        title_label = ttk.Label(header_frame, 
                               text="� Character Templates Gallery", 
                               font=("Segoe UI", 20, "bold"))
        title_label.pack(anchor="w")
        
        # Subtitle with better spacing
        subtitle_label = ttk.Label(header_frame,
                                  text=f"✨ Discover {len(self.templates_data)} unique character archetypes with rich lore",
                                  font=("Segoe UI", 11),
                                  foreground="#7f8c8d")
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        
        # Modern separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", padx=25, pady=15)
        
        # Enhanced content area with better padding
        content_frame = ttk.Frame(main_frame, relief="flat")
        content_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))
        
        # Enhanced scrolled text widget with modern styling
        self.text_widget = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#fafbfc",
            fg="#2c3e50",
            selectbackground="#3498db",
            selectforeground="white",
            padx=20,
            pady=20,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightcolor="#3498db",
            highlightbackground="#bdc3c7"
        )
        self.text_widget.pack(fill="both", expand=True)
        
        # Build enhanced template information
        self._populate_rich_template_view()
        
        # Enhanced footer with modern button design
        footer_frame = ttk.Frame(main_frame, relief="flat")
        footer_frame.pack(fill="x", padx=25, pady=(15, 25))
        
        # Modern separator
        separator2 = ttk.Separator(footer_frame, orient="horizontal")
        separator2.pack(fill="x", pady=(0, 20))
        
        # Enhanced button frame with better layout
        button_frame = ttk.Frame(footer_frame)
        button_frame.pack(fill="x", pady=10)
        
        # Action buttons with improved visibility
        self.use_template_button = ttk.Button(button_frame,
                                            text="⚔️ Create Character",
                                            command=self._create_from_selection,
                                            state="normal")  # Always enabled since templates are loaded
        self.use_template_button.pack(side="left", padx=(0, 15))
        
        # Refresh button
        refresh_button = ttk.Button(button_frame,
                                  text="🔄 Refresh Templates",
                                  command=self._refresh_templates)
        refresh_button.pack(side="left", padx=(0, 15))
        
        # Info label with better styling
        info_label = ttk.Label(button_frame, 
                              text=f"📋 {len(self.templates_data)} templates ready • Click Create Character to start",
                              font=("Segoe UI", 9),
                              foreground="#7f8c8d")
        info_label.pack(side="right", padx=15)
        
        # Store widgets in tab state for later access
        tab_state.widgets.update({
            'text_widget': self.text_widget,
            'use_template_button': self.use_template_button
        })
        
        return main_frame
    
    def _populate_rich_template_view(self) -> None:
        """Populate the rich template view with the same beautiful formatting as original"""
        if not self.templates_data:
            self.text_widget.insert(tk.END, "No character templates found.", "normal")
            return
        
        # Build formatted template information (exact same as original popup)
        for i, (name, info) in enumerate(self.templates_data.items()):
            character_class = info.get("character_class", "Unknown")
            description = info.get("description", "No description available")
            rarity = info.get("rarity", "COMMON")
            stats = info.get("stats") or info.get("base_stats") or {}
            starting_equipment = info.get("starting_equipment", [])
            starting_skills = info.get("starting_skills", [])
            
            # Template header
            self.text_widget.insert(tk.END, f"⚔️ {name.replace('_', ' ').title()}\n", "header")
            self.text_widget.insert(tk.END, f"Class: {character_class} | Rarity: {rarity}\n", "subheader")
            self.text_widget.insert(tk.END, "─" * 60 + "\n", "separator")
            
            # Description
            self.text_widget.insert(tk.END, f"📖 Description:\n", "section")
            self.text_widget.insert(tk.END, f"{description}\n\n", "normal")
            
            # Stats
            if stats:
                self.text_widget.insert(tk.END, f"📊 Base Statistics:\n", "section")
                sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
                for stat, value in sorted_stats:
                    self.text_widget.insert(tk.END, f"  • {stat.title()}: {value}\n", "stats")
                self.text_widget.insert(tk.END, "\n")
            
            # Starting Equipment
            if starting_equipment:
                self.text_widget.insert(tk.END, f"⚔️ Starting Equipment:\n", "section")
                for item in starting_equipment:
                    self.text_widget.insert(tk.END, f"  • {item.replace('_', ' ').title()}\n", "equipment")
                self.text_widget.insert(tk.END, "\n")
            
            # Starting Skills
            if starting_skills:
                self.text_widget.insert(tk.END, f"🎯 Starting Skills:\n", "section")
                for skill in starting_skills:
                    self.text_widget.insert(tk.END, f"  • {skill.replace('_', ' ').title()}\n", "skills")
                self.text_widget.insert(tk.END, "\n")
            
            # Add separator between templates
            if i < len(self.templates_data) - 1:
                self.text_widget.insert(tk.END, "═" * 80 + "\n\n", "divider")
        
        # Configure text tags for the same beautiful styling as original
        self.text_widget.tag_configure("header", font=("Segoe UI", 14, "bold"), foreground="#2c3e50")
        self.text_widget.tag_configure("subheader", font=("Segoe UI", 10), foreground="#7f8c8d")
        self.text_widget.tag_configure("separator", foreground="#bdc3c7")
        self.text_widget.tag_configure("section", font=("Segoe UI", 11, "bold"), foreground="#3498db")
        self.text_widget.tag_configure("normal", font=("Segoe UI", 10), foreground="#34495e")
        self.text_widget.tag_configure("stats", font=("Consolas", 10), foreground="#27ae60")
        self.text_widget.tag_configure("equipment", font=("Segoe UI", 10), foreground="#e67e22")
        self.text_widget.tag_configure("skills", font=("Segoe UI", 10), foreground="#9b59b6")
        self.text_widget.tag_configure("divider", foreground="#ecf0f1")
        
        # Make text read-only
        self.text_widget.configure(state="disabled")
        
        # Enable create button since we have templates
        if hasattr(self, 'use_template_button') and self.use_template_button:
            self.use_template_button.config(state="normal")
    
    def _create_from_selection(self) -> None:
        """Create character - switch directly to character creation tab"""
        if hasattr(self.ui_manager, 'switch_to_character_creation'):
            self.ui_manager.switch_to_character_creation()
            logger.info("Switching to character creation tab")
        else:
            messagebox.showinfo("Character Creation", 
                              "Character creation tab will be available soon!")
    
    def _refresh_templates(self) -> None:
        """Refresh the templates data"""
        self._load_templates()
        
        # Clear and repopulate the rich view
        if self.text_widget:
            self.text_widget.config(state="normal")
            self.text_widget.delete(1.0, tk.END)
            self._populate_rich_template_view()
        
        # Update tab title if manager available
        if hasattr(self.ui_manager, 'update_tab_title'):
            info = self.get_tab_info()
            self.ui_manager.update_tab_title('browse_templates', info['title'])
    
    def on_tab_activated(self, tab_state: TabState) -> None:
        """Called when tab becomes active"""
        logger.info("Browse Templates tab activated")
        # Refresh data when tab becomes active
        if self.templates_data is None:
            self._refresh_templates()
    
    def on_tab_deactivated(self, tab_state: TabState) -> None:
        """Called when tab becomes inactive"""
        logger.info("Browse Templates tab deactivated")
    
    def get_commands(self) -> Dict[str, Callable]:
        """Return tab-specific commands"""
        return {
            'refresh_templates': self._refresh_templates,
            'create_from_selection': self._create_from_selection
        }
